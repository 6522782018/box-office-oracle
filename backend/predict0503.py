# predict_next_sequel_from_history.py
# Task: classify Profit vs Loss of sequel k using ONLY history (1..k-1) within each franchise
# Split: for each franchise (Color + SeriesID), LAST available sequel-prediction sample -> TEST
# Change requested: keep the previous code structure, but set XGBoost threshold (thr) = 0.65 (XGBoost only)

import os
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, balanced_accuracy_score
)

# Optional XGBoost
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except Exception:
    HAS_XGBOOST = False


# =========================
# CONFIG
# =========================
RANDOM_SEED = 42

# ✅ Use pre-split train/test CSVs where each franchise (Color+SeriesID)
#    stays entirely in exactly one side.
TRAIN_FILE = "train_group_balanced.csv"
TEST_FILE  = "test_group_balanced.csv"

RAW_NUM_COLS = ["Gross_num", "Budget_num", "Sentiment", "IMDB_num"]
TARGET_PROFIT_COL = "Profit_num"   # numeric profit column
LABEL_COL = "ProfitLabel"          # 1=profit, 0=loss

# ✅ Set fixed threshold for XGBoost only
XGB_THR = 0.65


# =========================
# HELPERS
# =========================
def clean_currency(v):
    if isinstance(v, str):
        s = v.replace("$", "").replace(",", "").strip()
        if "(" in s and ")" in s:
            s = s.replace("(", "-").replace(")", "")
        return pd.to_numeric(s, errors="coerce")
    return pd.to_numeric(v, errors="coerce")


def find_sentiment_col(df: pd.DataFrame) -> str:
    candidates = ["Sentiment Analysis Score"]
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(f"Sentiment column not found. Tried: {candidates}")


def prepare_dataframe(csv_path: str) -> pd.DataFrame:
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

    if TARGET_PROFIT_COL not in df.columns:
        if "Ticket Profit" in df.columns:
            df[TARGET_PROFIT_COL] = df["Ticket Profit"].apply(clean_currency)
        else:
            raise ValueError(f"Missing {TARGET_PROFIT_COL} (or Ticket Profit)")

    sent_col = find_sentiment_col(df)
    df["Sentiment"] = pd.to_numeric(df[sent_col], errors="coerce")

    if "IMDB score" in df.columns:
        df["IMDB_num"] = pd.to_numeric(df["IMDB score"], errors="coerce")
    elif "IMDB" in df.columns:
        df["IMDB_num"] = pd.to_numeric(df["IMDB"], errors="coerce")
    else:
        raise ValueError("Missing IMDB score column (IMDB score / IMDB).")

    for c in RAW_NUM_COLS + [TARGET_PROFIT_COL]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    parts = df["ID_Year_Color"].astype(str).str.split("_", expand=True)
    if parts.shape[1] < 3:
        raise ValueError("ID_Year_Color must look like '1_2_O' (SeriesID_SequelNo_Color).")

    df["SeriesID"] = pd.to_numeric(parts[0], errors="coerce")
    df["SequelNo"] = pd.to_numeric(parts[1], errors="coerce")
    df["Color"] = parts[2].astype(str)

    df = df.dropna(subset=["SeriesID", "SequelNo"]).copy()
    df["SeriesID"] = df["SeriesID"].astype(int)
    df["SequelNo"] = df["SequelNo"].astype(int)

    df = df.dropna(subset=RAW_NUM_COLS + [TARGET_PROFIT_COL]).copy()

    df[LABEL_COL] = (df[TARGET_PROFIT_COL] > 0).astype(int)
    return df


def build_history_supervised(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["Color", "SeriesID"]

    for (color, sid), g in df.groupby(group_cols):
        g = g.sort_values("SequelNo").reset_index(drop=True)
        if len(g) < 2:
            continue

        for i in range(1, len(g)):
            hist = g.iloc[:i]
            target = g.iloc[i]

            prev_gross = hist["Gross_num"].iloc[-1]
            prev_budget = hist["Budget_num"].iloc[-1]
            prev_sent = hist["Sentiment"].iloc[-1]
            prev_imdb = hist["IMDB_num"].iloc[-1]

            avg_gross = hist["Gross_num"].mean()
            avg_budget = hist["Budget_num"].mean()
            avg_sent = hist["Sentiment"].mean()
            avg_imdb = hist["IMDB_num"].mean()

            if len(hist) >= 2:
                trend_gross = hist["Gross_num"].iloc[-1] - hist["Gross_num"].iloc[0]
                trend_budget = hist["Budget_num"].iloc[-1] - hist["Budget_num"].iloc[0]
                trend_sent = hist["Sentiment"].iloc[-1] - hist["Sentiment"].iloc[0]
                trend_imdb = hist["IMDB_num"].iloc[-1] - hist["IMDB_num"].iloc[0]
            else:
                trend_gross = 0.0
                trend_budget = 0.0
                trend_sent = 0.0
                trend_imdb = 0.0

            rows.append({
                "Color": color,
                "SeriesID": sid,
                "TargetSequelNo": int(target["SequelNo"]),
                "HistoryLen": int(len(hist)),

                "prev_gross": prev_gross,
                "prev_budget": prev_budget,
                "prev_sentiment": prev_sent,
                "prev_imdb": prev_imdb,

                "avg_gross": avg_gross,
                "avg_budget": avg_budget,
                "avg_sentiment": avg_sent,
                "avg_imdb": avg_imdb,

                "trend_gross": trend_gross,
                "trend_budget": trend_budget,
                "trend_sentiment": trend_sent,
                "trend_imdb": trend_imdb,

                "y": int(target[LABEL_COL])
            })

    return pd.DataFrame(rows)


FEATURE_COLS = [
    "TargetSequelNo", "HistoryLen",
    "prev_gross", "prev_budget", "prev_sentiment", "prev_imdb",
    "avg_gross", "avg_budget", "avg_sentiment", "avg_imdb",
    "trend_gross", "trend_budget", "trend_sentiment", "trend_imdb"
]


def last_counts_by_franchise(df: pd.DataFrame) -> pd.Series:
    """Count unique franchises per Color (for display)."""
    return df.groupby("Color")["SeriesID"].nunique().sort_index()


def latest_label_counts(df: pd.DataFrame) -> pd.Series:
    """Counts ProfitLabel of the latest (max SequelNo) movie per franchise."""
    idx_last = df.groupby(["Color", "SeriesID"])["SequelNo"].idxmax()
    last = df.loc[idx_last, ["Color", "SeriesID", LABEL_COL]].copy()
    return last[LABEL_COL].value_counts().sort_index()  # 0 then 1


def eval_classifier(name, model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)

    # ✅ Apply threshold only for XGBoost
    if ("XGBoost" in name) and hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_test)[:, 1]
        pred = (proba >= XGB_THR).astype(int)
    else:
        pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)
    bal_acc = balanced_accuracy_score(y_test, pred)
    prec = precision_score(y_test, pred, zero_division=0)
    rec = recall_score(y_test, pred, zero_division=0)
    f1_pos = f1_score(y_test, pred, zero_division=0)
    f1_macro = f1_score(y_test, pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_test, pred)

    print(f"\n{name}" + (f"  (XGB thr={XGB_THR})" if "XGBoost" in name else ""))
    print(f"Accuracy        : {acc:.4f}")
    print(f"Balanced Acc    : {bal_acc:.4f}")
    print(f"Precision (pos) : {prec:.4f}")
    print(f"Recall (pos)    : {rec:.4f}")
    print(f"F1 (pos)        : {f1_pos:.4f}")
    print(f"F1 (macro)      : {f1_macro:.4f}")
    print("Confusion Matrix [ [TN FP] [FN TP] ]:")
    print(cm)

    return (name, acc, bal_acc, prec, rec, f1_pos, f1_macro)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(base_dir, TRAIN_FILE)
    test_path  = os.path.join(base_dir, TEST_FILE)

    if not os.path.exists(train_path):
        raise FileNotFoundError(
            f"Train CSV not found: {train_path}\n"
            f"Put '{TRAIN_FILE}' next to this .py file, or change TRAIN_FILE."
        )
    if not os.path.exists(test_path):
        raise FileNotFoundError(
            f"Test CSV not found: {test_path}\n"
            f"Put '{TEST_FILE}' next to this .py file, or change TEST_FILE."
        )

    # 1) Load raw movies (all sequels) for each side
    df_train_raw = prepare_dataframe(train_path)
    df_test_raw  = prepare_dataframe(test_path)

    # Sanity: no franchise overlap across splits
    tr_keys = set(zip(df_train_raw["Color"], df_train_raw["SeriesID"]))
    te_keys = set(zip(df_test_raw["Color"], df_test_raw["SeriesID"]))
    overlap = tr_keys & te_keys
    if overlap:
        raise ValueError(
            f"Franchise overlap detected between train and test (showing up to 5): {list(overlap)[:5]}"
        )

    # 2) Build supervised samples separately per side
    train_df = build_history_supervised(df_train_raw)
    test_df  = build_history_supervised(df_test_raw)

    print("\n=== Franchise counts (unique SeriesID per Color) ===")
    print("TRAIN")
    print(last_counts_by_franchise(df_train_raw).to_string())
    print("\nTEST")
    print(last_counts_by_franchise(df_test_raw).to_string())

    print("\n=== Latest sequel label counts per franchise (0=loss,1=profit) ===")
    print("TRAIN")
    print(latest_label_counts(df_train_raw).to_string())
    print("\nTEST")
    print(latest_label_counts(df_test_raw).to_string())

    print(f"\nSupervised rows (TRAIN): {len(train_df)}")
    print(f"Supervised rows (TEST) : {len(test_df)}")

    print(f"\nTRAIN %Profit (supervised y): {train_df['y'].mean()*100:.2f}%")
    print(f"TEST  %Profit (supervised y): {test_df['y'].mean()*100:.2f}%")

    train_df.to_csv("train_history_split.csv", index=False)
    test_df.to_csv("test_history_split.csv", index=False)

    X_train = train_df[FEATURE_COLS].values
    y_train = train_df["y"].values

    X_test = test_df[FEATURE_COLS].values
    y_test = test_df["y"].values

    models = [
        ("Logistic Regression", Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                max_iter=5000,
                random_state=RANDOM_SEED,
                class_weight="balanced"
            ))
        ])),

        ("Decision Tree", DecisionTreeClassifier(
            max_depth=8,
            random_state=RANDOM_SEED,
            class_weight="balanced"
        )),

        ("Random Forest", RandomForestClassifier(
            n_estimators=400,
            max_depth=14,
            random_state=RANDOM_SEED,
            class_weight="balanced_subsample"
        )),

        ("MLP Classifier", Pipeline([
            ("scaler", StandardScaler()),
            ("clf", MLPClassifier(
                hidden_layer_sizes=(64, 32),
                alpha=1e-4,
                learning_rate_init=1e-3,
                max_iter=3000,
                random_state=RANDOM_SEED
            ))
        ])),
    ]

    if HAS_XGBOOST:
        pos = train_df["y"].sum()
        neg = len(train_df) - pos
        scale_pos_weight = (neg / pos) if pos > 0 else 1.0

        models.append((
            "XGBoost Classifier",
            XGBClassifier(
                n_estimators=600,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=RANDOM_SEED,
                eval_metric="logloss",
                scale_pos_weight=scale_pos_weight
            )
        ))
    else:
        print("\nXGBoost not available. Install with: pip install xgboost")

    results = []
    for name, model in models:
        results.append(eval_classifier(name, model, X_train, y_train, X_test, y_test))

    results_df = pd.DataFrame(
        results,
        columns=["Model", "Accuracy", "BalancedAcc", "Precision", "Recall", "F1_pos", "F1_macro"]
    ).sort_values(["F1_macro", "BalancedAcc"], ascending=False)

    print("\n=== Summary (sorted by F1_macro, then BalancedAcc) ===")
    print(results_df.to_string(index=False))

    best_model_name = results_df.iloc[0]["Model"]
    print(f"\nBest model by F1_macro: {best_model_name}")