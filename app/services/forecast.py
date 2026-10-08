"""Demand-model loading, feature creation, and recursive monthly forecasting."""

from calendar import monthrange
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "year", "month", "day_of_week", "is_weekend", "is_back_to_school",
    "is_holiday_season", "lag_1", "lag_7", "rolling_mean_7", "rolling_mean_30",
    "is_promo", "is_stockout",
]

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT_DIR / "models" / "stacking_model_v3.joblib"
DATA_PATH = ROOT_DIR / "data" / "raw" / "demand_timeseries_v3.csv"


def load_bundle(path: str | Path = MODEL_PATH) -> dict:
    """Load the trained model bundle from disk."""
    return joblib.load(path)


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Build the exact calendar and lag features used during training."""
    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"])
    result = result.sort_values(["sku_id", "date"]).reset_index(drop=True)
    result["year"] = result["date"].dt.year
    result["month"] = result["date"].dt.month
    result["day_of_week"] = result["date"].dt.dayofweek
    result["is_weekend"] = result["day_of_week"].isin([5, 6]).astype(int)
    result["is_back_to_school"] = result["month"].isin([8, 9]).astype(int)
    result["is_holiday_season"] = result["month"].isin([11, 12]).astype(int)
    result["is_promo"] = result.get("is_promo", 0)
    result["is_stockout"] = result.get("is_stockout", 0)
    result["lag_1"] = result.groupby("sku_id")["units_sold"].shift(1)
    result["lag_7"] = result.groupby("sku_id")["units_sold"].shift(7)
    result["rolling_mean_7"] = result.groupby("sku_id")["units_sold"].transform(lambda x: x.shift(1).rolling(7).mean())
    result["rolling_mean_30"] = result.groupby("sku_id")["units_sold"].transform(lambda x: x.shift(1).rolling(30).mean())
    result["units_sold_diff"] = result["units_sold"] - result["lag_1"]
    return result


def forecast_month(year: int, month: int, promo: bool = False, stockout: bool = False) -> pd.DataFrame:
    """Forecast every day and SKU for a selected month using recursive features."""
    bundle = load_bundle()
    history = pd.read_csv(DATA_PATH, parse_dates=["date"])
    history = history.sort_values(["sku_id", "date"]).copy()
    outputs = []
    days = monthrange(year, month)[1]
    for sku_id in bundle["skus"]:
        sku_history = history[history["sku_id"] == sku_id].copy()
        values = list(sku_history["units_sold"].astype(float))
        dates = list(sku_history["date"])
        for day in range(1, days + 1):
            current = pd.Timestamp(date(year, month, day))
            recent = values[-30:]
            row = {
                "date": current, "sku_id": sku_id, "units_sold": values[-1],
                "is_promo": int(promo), "is_stockout": int(stockout),
            }
            row_df = pd.DataFrame([row])
            row_df["year"] = current.year
            row_df["month"] = current.month
            row_df["day_of_week"] = current.dayofweek
            row_df["is_weekend"] = int(current.dayofweek in [5, 6])
            row_df["is_back_to_school"] = int(current.month in [8, 9])
            row_df["is_holiday_season"] = int(current.month in [11, 12])
            row_df["lag_1"] = values[-1]
            row_df["lag_7"] = values[-7] if len(values) >= 7 else float(np.mean(values))
            row_df["rolling_mean_7"] = float(np.mean(values[-7:]))
            row_df["rolling_mean_30"] = float(np.mean(recent))
            features = row_df[FEATURE_COLUMNS]
            models = bundle["models"][sku_id]
            base = np.column_stack([models["cat"].predict(features), models["xgb"].predict(features), models["lgb"].predict(features)])
            meta_input = np.column_stack([base, row_df[["is_promo", "is_weekend", "is_stockout"]].values])
            diff = float(models["meta"].predict(meta_input)[0])
            predicted = max(0.0, values[-1] + diff)
            values.append(predicted)
            dates.append(current)
            outputs.append({"date": current, "sku_id": sku_id, "forecast_units": predicted})
    result = pd.DataFrame(outputs)
    return result
