# Production Planning Optimisation

A beginner-friendly Streamlit application for laptop demand forecasting, raw-material planning, and order tracking.

## Features

- Trained v3 stacking model: CatBoost + XGBoost + LightGBM with positive Ridge meta-model
- Recursive daily forecasts reconstructed from the differenced target
- Monthly SKU overrides
- BOM-based material requirements
- 10% editable safety stock
- MOQ rounding and lead-time warnings
- Editable order quantities and cost impact
- SQLite order history with status updates and receipt-to-stock logic
- Editable material, MOQ, cost, lead-time, and stock settings

## Quick start on Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

Open `http://localhost:8501`.

## Project layout

```text
app.py                    # Streamlit entry point
train_model.py            # Model training command
pages/                    # Streamlit pages
app/services/             # Forecast, planning, and order services
app/db/                   # SQLAlchemy models, database, seed data
models/                   # Saved trained model bundle
data/                     # Repository data and features
```

## Mentor demo flow

1. Open the dashboard and show model validation metrics.
2. Open **Sales Forecast**, click **Predict**, and edit one SKU forecast.
3. Open **Raw Material Planning**, change one final order quantity, and show cost impact.
4. Click **Place Order**.
5. Open **Order History**, change the order to **Received**, and show stock update.
6. Open **Settings** to demonstrate editable costs, MOQs, lead times, and stock.

## Deployment note

GitHub Pages hosts static HTML and cannot run a Python Streamlit backend. The complete source and model are stored in GitHub, but the working application should be run locally or deployed to Streamlit Community Cloud, Render, Railway, or another Python-capable host. GitHub Pages can be used for this README and project documentation only.
