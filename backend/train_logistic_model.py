"""
train_logistic_for_web.py

Purpose:
- Keep original predict0503.py unchanged.
- Import helper functions/constants from predict0503.py.
- Train ONLY Logistic Regression.
- Save model as logistic_model.pkl.
- Save feature columns as feature_cols.json.

Put this file in the SAME folder as:
- predict0503.py
- train_group_balanced.csv

Run:
    python3 train_logistic_for_web.py
"""

import os
import json
import sys
import glob
import importlib
from datetime import datetime

import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


RANDOM_SEED = None
TRAIN_FILE = None
FEATURE_COLS = None
prepare_dataframe = None
build_history_supervised = None


LOG_PATH = "/Users/poramatesuphanklang/Documents/base44 + ML/box-office-oracle/.cursor/debug-4c3bf3.log"


def debug_log(hypothesis_id: str, location: str, message: str, data: dict):
    payload = {
        "sessionId": "4c3bf3",
        "runId": "initial",
        "hypothesisId": hypothesis_id,
        "id": f"log_{datetime.utcnow().timestamp()}",
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.utcnow().timestamp() * 1000),
    }

    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except Exception:
        pass


def resolve_data_path(base_dir: str, filename: str, hypothesis_id: str) -> str:
    candidates = [
        os.path.join(base_dir, filename),
        os.path.join("/Users/poramatesuphanklang/Documents/ML Project Final", filename),
        os.path.join(
            "/Users/poramatesuphanklang/Documents/base44 + ML/box-office-oracle/public",
            filename,
        ),
    ]

    existing = [p for p in candidates if os.path.exists(p)]

    debug_log(
        hypothesis_id,
        "train_logistic_for_web.py:resolve_data_path",
        "Resolving required data file",
        {
            "filename": filename,
            "candidates": candidates,
            "existing": existing,
        },
    )

    if existing:
        return existing[0]

    return os.path.join(base_dir, filename)


def load_predict_dependencies(base_dir: str):
    global RANDOM_SEED, TRAIN_FILE, FEATURE_COLS
    global prepare_dataframe, build_history_supervised

    debug_log(
        "H1",
        "train_logistic_for_web.py:load_predict_dependencies",
        "Starting dependency import diagnostics",
        {
            "base_dir": base_dir,
            "cwd": os.getcwd(),
            "sys_path_head": sys.path[:5],
            "candidate_files": glob.glob(os.path.join(base_dir, "predict0503*.py")),
        },
    )

    module_name = "predict0503"

    try:
        module = importlib.import_module(module_name)

        debug_log(
            "H1",
            "train_logistic_for_web.py:load_predict_dependencies",
            "Imported primary module successfully",
            {
                "module_name": module_name,
                "module_file": getattr(module, "__file__", ""),
            },
        )

    except ModuleNotFoundError as e:
        debug_log(
            "H2",
            "train_logistic_for_web.py:load_predict_dependencies",
            "Primary import failed; attempting fallback",
            {
                "module_name": module_name,
                "error_type": type(e).__name__,
                "error": str(e),
            },
        )

        module_name = "predict05031"
        module = importlib.import_module(module_name)

        debug_log(
            "H4",
            "train_logistic_for_web.py:load_predict_dependencies",
            "Imported fallback module successfully",
            {
                "module_name": module_name,
                "module_file": getattr(module, "__file__", ""),
            },
        )

    except Exception as e:
        debug_log(
            "H2",
            "train_logistic_for_web.py:load_predict_dependencies",
            "Import failed with non-ModuleNotFoundError",
            {
                "error_type": type(e).__name__,
                "error": str(e),
            },
        )
        raise

    RANDOM_SEED = module.RANDOM_SEED
    TRAIN_FILE = module.TRAIN_FILE
    FEATURE_COLS = module.FEATURE_COLS
    prepare_dataframe = module.prepare_dataframe
    build_history_supervised = module.build_history_supervised

    debug_log(
        "H3",
        "train_logistic_for_web.py:load_predict_dependencies",
        "Dependency symbols loaded",
        {
            "train_file": TRAIN_FILE,
            "feature_cols_count": len(FEATURE_COLS) if FEATURE_COLS else 0,
        },
    )


MODEL_FILE = "logistic_model.pkl"
FEATURE_FILE = "feature_cols.json"


def train_logistic_model(base_dir: str):
    train_path = resolve_data_path(base_dir, TRAIN_FILE, "H6")

    if not os.path.exists(train_path):
        debug_log(
            "H6",
            "train_logistic_for_web.py:train_logistic_model",
            "Train file still not found after path resolution",
            {
                "train_file": TRAIN_FILE,
                "resolved_path": train_path,
            },
        )

        raise FileNotFoundError(f"Train file not found: {train_path}")

    # Use your original cleaning + history feature engineering from predict0503.py
    df_train_raw = prepare_dataframe(train_path)
    train_df = build_history_supervised(df_train_raw)

    if train_df.empty:
        raise ValueError("No supervised training rows were created. Check train CSV data.")

    X_train = train_df[FEATURE_COLS].values
    y_train = train_df["y"].values

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            max_iter=5000,
            random_state=RANDOM_SEED,
            class_weight="balanced",
        )),
    ])

    model.fit(X_train, y_train)

    model_path = os.path.join(base_dir, MODEL_FILE)
    feature_path = os.path.join(base_dir, FEATURE_FILE)

    joblib.dump(model, model_path)

    with open(feature_path, "w", encoding="utf-8") as f:
        json.dump(FEATURE_COLS, f, indent=2)

    print(f"Saved model: {model_path}")
    print(f"Saved features: {feature_path}")
    print(f"Training rows: {len(train_df)}")

    return model


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    load_predict_dependencies(BASE_DIR)
    final_model = train_logistic_model(BASE_DIR)

    print("\nDone.")
    print("This script only creates:")
    print(f"- {MODEL_FILE}")
    print(f"- {FEATURE_FILE}")