# train_xgboost_model.py

"""
Purpose:
- Keep original predict0503.py unchanged.
- Import helper functions/constants from predict0503.py.
- Train ONLY XGBoost Classifier.
- Save model package as xgboost_model.pkl.
- Use the same feature columns and threshold as predict0503.py.

Put this file in the SAME folder as:
- predict0503.py
- train_group_balanced.csv

Run:
    python3 train_xgboost_model.py
"""

import os
import pickle

from xgboost import XGBClassifier

# Import functions/settings from predict0503.py
from predict0503 import (
    prepare_dataframe,
    build_history_supervised,
    FEATURE_COLS,
    RANDOM_SEED,
    XGB_THR,
    TRAIN_FILE,
)


OUTPUT_MODEL_FILE = "xgboost_model.pkl"


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    train_path = os.path.join(base_dir, TRAIN_FILE)

    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Train file not found: {train_path}")

    # 1. Load and clean training data using the same logic as predict0503.py
    df_train_raw = prepare_dataframe(train_path)

    # 2. Build history-based supervised training data
    train_df = build_history_supervised(df_train_raw)

    if train_df.empty:
        raise ValueError("No supervised training rows were created. Check train CSV data.")

    print("Train supervised rows:", len(train_df))

    # 3. Prepare input features and target labels$
    X_train = train_df[FEATURE_COLS].values
    y_train = train_df["y"].values

    # 4. Calculate class weight for XGBoost
    # This helps handle imbalance between Profit and Loss classes.
    pos = train_df["y"].sum()
    neg = len(train_df) - pos
    scale_pos_weight = (neg / pos) if pos > 0 else 1.0

    # 5. Create XGBoost model with the same settings as predict0503.py
    model = XGBClassifier(
        n_estimators=600,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
    )

    # 6. Train model
    model.fit(X_train, y_train)

    # 7. Save model with important settings for backend prediction
    model_package = {
        "model": model,
        "feature_cols": FEATURE_COLS,
        "threshold": XGB_THR,
        "model_type": "XGBoost Classifier",
    }

    output_path = os.path.join(base_dir, OUTPUT_MODEL_FILE)

    with open(output_path, "wb") as f:
        pickle.dump(model_package, f)

    print(f"\nSaved XGBoost model to: {output_path}")
    print(f"Threshold saved: {XGB_THR}")
    print("Feature columns:")
    for col in FEATURE_COLS:
        print("-", col)

    print("\nDone.")
    print("This script only creates:")
    print(f"- {OUTPUT_MODEL_FILE}")


if __name__ == "__main__":
    main()