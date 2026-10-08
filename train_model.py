"""Train and save the production-planning stacking model."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor

from app.services.forecast import FEATURE_COLUMNS, ROOT_DIR, make_features


DATA_PATH = ROOT_DIR / "data" / "raw" / "demand_timeseries_v3.csv"
MODEL_PATH = ROOT_DIR / "models" / "stacking_model_v3.joblib"


def train_models() -> dict:
    """Train one stacking ensemble per SKU and return a serialisable bundle."""
    raw = pd.read_csv(DATA_PATH, parse_dates=["date"])
    frame = make_features(raw).dropna().reset_index(drop=True)
    bundle = {"version": "v3-positive-ridge", "feature_columns": FEATURE_COLUMNS, "skus": sorted(frame["sku_id"].unique()), "models": {}, "metrics": {}}
    for sku_id in bundle["skus"]:
        sku = frame[frame["sku_id"] == sku_id].sort_values("date").reset_index(drop=True)
        train_idx = int(len(sku) * 0.8)
        train = sku.iloc[:train_idx]
        test = sku.iloc[train_idx:]
        x_train = train[FEATURE_COLUMNS]
        y_train = train["units_sold_diff"]
        cat = CatBoostRegressor(iterations=250, depth=6, learning_rate=0.05, random_seed=42, verbose=False)
        xgb = XGBRegressor(n_estimators=250, max_depth=6, learning_rate=0.05, random_state=42, n_jobs=2, objective="reg:squarederror")
        lgb = LGBMRegressor(n_estimators=250, learning_rate=0.05, random_state=42, verbose=-1, n_jobs=2)
        cat.fit(x_train, y_train)
        xgb.fit(x_train, y_train)
        lgb.fit(x_train, y_train)
        base_train = np.column_stack([cat.predict(x_train), xgb.predict(x_train), lgb.predict(x_train)])
        meta_features = np.column_stack([base_train, train[["is_promo", "is_weekend", "is_stockout"]].values])
        meta = Ridge(alpha=1.0, positive=True)
        meta.fit(meta_features, y_train)
        models = {"cat": cat, "xgb": xgb, "lgb": lgb, "meta": meta}
        bundle["models"][sku_id] = models
        if len(test):
            base_test = np.column_stack([cat.predict(test[FEATURE_COLUMNS]), xgb.predict(test[FEATURE_COLUMNS]), lgb.predict(test[FEATURE_COLUMNS])])
            test_meta = np.column_stack([base_test, test[["is_promo", "is_weekend", "is_stockout"]].values])
            actual = np.maximum(0, test["lag_1"].values + meta.predict(test_meta))
            bundle["metrics"][sku_id] = {"mae": float(np.mean(np.abs(test["units_sold"].values - actual))), "rmse": float(np.sqrt(np.mean((test["units_sold"].values - actual) ** 2)))}
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(bundle, MODEL_PATH)
    return bundle


if __name__ == "__main__":
    result = train_models()
    print(f"Saved model to {MODEL_PATH}")
    print("SKUs:", ", ".join(result["skus"]))
    print("Metrics:", result["metrics"])
