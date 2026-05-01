from flask import Flask, request, jsonify
from flask_cors import CORS
from custom_predict import build_custom_features
import pandas as pd
import numpy as np
import joblib
import os
import traceback

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGISTIC_MODEL_PATH = os.path.join(BASE_DIR, "logistic_model.pkl")
XGBOOST_MODEL_PATH = os.path.join(BASE_DIR, "xgboost_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "Coded_MovieDataCollect_filled_sentiment_.csv")

def load_model_from_pkl(path):
    loaded = joblib.load(path)

    # If the pkl is already a model
    if hasattr(loaded, "predict"):
        return loaded

    # If the pkl is saved as a dictionary
    if isinstance(loaded, dict):
        possible_keys = [
            "model",
            "xgboost_model",
            "xgb_model",
            "classifier",
            "clf",
            "pipeline",
        ]

        for key in possible_keys:
            if key in loaded and hasattr(loaded[key], "predict"):
                return loaded[key]

        raise ValueError(
            f"Model file is a dictionary, but no usable model was found. "
            f"Available keys: {list(loaded.keys())}"
        )

    raise ValueError(f"Unsupported model file type: {type(loaded)}")


logistic_model = load_model_from_pkl(LOGISTIC_MODEL_PATH)
xgboost_model = load_model_from_pkl(XGBOOST_MODEL_PATH)

XGB_THRESHOLD = 0.65

FEATURE_COLS = [
    "TargetSequelNo",
    "HistoryLen",
    "prev_gross",
    "prev_budget",
    "prev_sentiment",
    "prev_imdb",
    "avg_gross",
    "avg_budget",
    "avg_sentiment",
    "avg_imdb",
    "trend_gross",
    "trend_budget",
    "trend_sentiment",
    "trend_imdb",
]


def clean_currency(value):
    if pd.isna(value):
        return np.nan

    if isinstance(value, str):
        value = (
            value.replace("$", "")
            .replace(",", "")
            .replace("(", "-")
            .replace(")", "")
            .strip()
        )

    return pd.to_numeric(value, errors="coerce")


def prepare_dataframe(csv_path):
    df = pd.read_csv(csv_path)

    if "ID_Year_Color" not in df.columns:
        raise ValueError("Missing required column: ID_Year_Color")

    df = df[df["ID_Year_Color"].notna()].copy()

    if "Budget_num" not in df.columns and "Budget" in df.columns:
        df["Budget_num"] = df["Budget"].apply(clean_currency)

    if "Gross_num" not in df.columns:
        if "Gross Worldwide" in df.columns:
            df["Gross_num"] = df["Gross Worldwide"].apply(clean_currency)
        elif "Gross" in df.columns:
            df["Gross_num"] = df["Gross"].apply(clean_currency)
        elif "Revenue" in df.columns:
            df["Gross_num"] = df["Revenue"].apply(clean_currency)
        else:
            raise ValueError(
                "Missing Gross column: Gross_num / Gross Worldwide / Gross / Revenue"
            )

    if "Profit_num" in df.columns:
        df["Profit_num"] = pd.to_numeric(df["Profit_num"], errors="coerce")
    elif "Ticket Profit" in df.columns:
        df["Profit_num"] = df["Ticket Profit"].apply(clean_currency)
    else:
        df["Profit_num"] = (df["Gross_num"] / 2) - df["Budget_num"]

    if "Sentiment Analysis Score" in df.columns:
        df["Sentiment"] = pd.to_numeric(
            df["Sentiment Analysis Score"], errors="coerce"
        )
    elif "Sentiment" in df.columns:
        df["Sentiment"] = pd.to_numeric(df["Sentiment"], errors="coerce")
    else:
        df["Sentiment"] = 0

    if "IMDB score" in df.columns:
        df["IMDB_num"] = pd.to_numeric(df["IMDB score"], errors="coerce")
    elif "IMDB" in df.columns:
        df["IMDB_num"] = pd.to_numeric(df["IMDB"], errors="coerce")
    else:
        df["IMDB_num"] = 0

    parts = df["ID_Year_Color"].astype(str).str.split("_", expand=True)

    if parts.shape[1] < 3:
        raise ValueError("ID_Year_Color must look like '1_2_O'")

    df["SeriesID"] = pd.to_numeric(parts[0], errors="coerce")
    df["SequelNo"] = pd.to_numeric(parts[1], errors="coerce")
    df["Color"] = parts[2].astype(str)

    df = df.dropna(
        subset=[
            "SeriesID",
            "SequelNo",
            "Gross_num",
            "Budget_num",
            "Profit_num",
            "Sentiment",
            "IMDB_num",
        ]
    ).copy()

    df["SeriesID"] = df["SeriesID"].astype(int)
    df["SequelNo"] = df["SequelNo"].astype(int)

    df["ProfitLabel"] = (df["Profit_num"] > 0).astype(int)

    return df


df_movies = prepare_dataframe(DATA_PATH)


def build_next_feature_row(history):
    history = history.sort_values("SequelNo")

    prev_gross = history["Gross_num"].iloc[-1]
    prev_budget = history["Budget_num"].iloc[-1]
    prev_sentiment = history["Sentiment"].iloc[-1]
    prev_imdb = history["IMDB_num"].iloc[-1]

    avg_gross = history["Gross_num"].mean()
    avg_budget = history["Budget_num"].mean()
    avg_sentiment = history["Sentiment"].mean()
    avg_imdb = history["IMDB_num"].mean()

    if len(history) >= 2:
        trend_gross = history["Gross_num"].iloc[-1] - history["Gross_num"].iloc[0]
        trend_budget = history["Budget_num"].iloc[-1] - history["Budget_num"].iloc[0]
        trend_sentiment = history["Sentiment"].iloc[-1] - history["Sentiment"].iloc[0]
        trend_imdb = history["IMDB_num"].iloc[-1] - history["IMDB_num"].iloc[0]
    else:
        trend_gross = 0
        trend_budget = 0
        trend_sentiment = 0
        trend_imdb = 0

    next_sequel_no = int(history["SequelNo"].max()) + 1

    row = {
        "TargetSequelNo": next_sequel_no,
        "HistoryLen": len(history),

        "prev_gross": prev_gross,
        "prev_budget": prev_budget,
        "prev_sentiment": prev_sentiment,
        "prev_imdb": prev_imdb,

        "avg_gross": avg_gross,
        "avg_budget": avg_budget,
        "avg_sentiment": avg_sentiment,
        "avg_imdb": avg_imdb,

        "trend_gross": trend_gross,
        "trend_budget": trend_budget,
        "trend_sentiment": trend_sentiment,
        "trend_imdb": trend_imdb,
    }

    return pd.DataFrame([row], columns=FEATURE_COLS)


@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        body = request.get_json()

        if body is None:
            return jsonify({"error": "Missing JSON body"}), 400

        query = body.get("query", "").strip().lower()
        selected_model = body.get("model", "logistic").strip().lower()

        if selected_model not in ["logistic", "xgboost"]:
            selected_model = "logistic"

        if not query:
            return jsonify({"error": "Missing search query"}), 400

        matched = df_movies[
            df_movies["Title"].astype(str).str.lower().str.contains(
                query, na=False, regex=False
            )
        ]

        if matched.empty:
            return jsonify({"error": "Franchise not found"}), 404

        first_match = matched.iloc[0]
        series_id = first_match["SeriesID"]
        color = first_match["Color"]

        franchise_movies = df_movies[
            (df_movies["SeriesID"] == series_id)
            & (df_movies["Color"] == color)
        ].sort_values("SequelNo")

        if franchise_movies.empty:
            return jsonify({"error": "No movies found for this franchise"}), 404

        X = build_next_feature_row(franchise_movies)

        if selected_model == "xgboost":
            active_model = xgboost_model
            model_display_name = "XGBoost"
            threshold = XGB_THRESHOLD

            probability_profit = float(active_model.predict_proba(X)[0][1])
            prediction_number = 1 if probability_profit >= XGB_THRESHOLD else 0

        else:
            active_model = logistic_model
            model_display_name = "Logistic Regression"
            threshold = 0.5

            if hasattr(active_model, "predict_proba"):
                probability_profit = float(active_model.predict_proba(X)[0][1])
            else:
                temp_prediction = int(active_model.predict(X)[0])
                probability_profit = 1.0 if temp_prediction == 1 else 0.0

            prediction_number = int(active_model.predict(X)[0])

        prediction = "Profit" if prediction_number == 1 else "Loss"

        movies = []

        for _, row in franchise_movies.iterrows():
            revenue = float(row["Gross_num"])
            budget = float(row["Budget_num"])
            profit = float(row["Profit_num"])

            roi = (profit / budget) * 100 if budget != 0 else 0

            movies.append({
                "title": str(row.get("Title", "")),
                "year": int(row.get("Year", 0)) if not pd.isna(row.get("Year", 0)) else 0,

                "budget": budget,
                "revenue": revenue,
                "gross": revenue,

                "profit": profit,
                "profit_loss": profit,
                "ticket_profit": profit,
                "roi": roi,
                "is_profit": profit > 0,

                "imdb": float(row["IMDB_num"]),
                "sentiment": float(row["Sentiment"]),
            })

        avg_budget = float(franchise_movies["Budget_num"].mean())
        avg_revenue = float(franchise_movies["Gross_num"].mean())
        avg_profit = float(franchise_movies["Profit_num"].mean())

        estimated_budget = avg_budget
        estimated_revenue = avg_revenue

        estimated_profit = (estimated_revenue / 2) - estimated_budget
        estimated_roi = (
            (estimated_profit / estimated_budget) * 100
            if estimated_budget != 0
            else 0
        )

        return jsonify({
            "franchiseName": query.title(),
            "movies": movies,
            "prediction": {
                "prediction": prediction.lower(),
                "label": prediction,

                "model": selected_model,
                "model_name": model_display_name,
                "threshold": threshold,

                "estimated_budget": round(estimated_budget),
                "estimated_revenue": round(estimated_revenue),
                "estimated_profit": round(estimated_profit),
                "estimated_roi": round(estimated_roi, 2),
                "average_existing_profit": round(avg_profit),

                "confidence": round(probability_profit * 100),
                "probability": round(probability_profit, 4),

                "reasoning": (
                    f"Prediction generated live using {model_display_name} from "
                    f"{len(franchise_movies)} previous movie(s). "
                    f"Existing movie profit/loss values are taken directly from Profit_num in the CSV."
                )
            }
        })

    except Exception as e:
        print("BACKEND ERROR:")
        print(traceback.format_exc())

        return jsonify({
            "error": "Backend prediction error",
            "details": str(e)
        }), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/custom-predict", methods=["POST"])
def custom_predict():
    try:
        data = request.get_json()

        model_type = data.get("model", "logistic")
        movies = data.get("movies", [])

        feature_row = build_custom_features(movies)

        if model_type == "xgboost":
            proba = xgboost_model.predict_proba(feature_row)[0][1]
            prediction = int(proba >= 0.65)
        else:
            proba = logistic_model.predict_proba(feature_row)[0][1]
            prediction = int(proba >= 0.5)

        return jsonify({
            "prediction": "Profit" if prediction == 1 else "Loss",
            "probability": round(float(proba), 3),
            "model": model_type,
            "sentiment_used": 52.76
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Box Office Oracle backend is running",
        "predict_endpoint": "/api/predict",
        "health_endpoint": "/api/health"
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)