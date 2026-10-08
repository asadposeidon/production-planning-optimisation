"""Main dashboard for the production planning application."""

from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy import func, select

from app.db.database import get_session
from app.db.models import Order
from app.db.seed import seed_database
from app.services.forecast import forecast_month, load_bundle
from app.ui import apply_theme, page_header

st.set_page_config(page_title="Production Planning Optimisation", page_icon="PP", layout="wide", initial_sidebar_state="expanded")
apply_theme()
seed_database()

page_header("Planning intelligence", "Production Planning Optimisation", "A clear view from demand forecast to material order.")
try:
    bundle = load_bundle()
    current = date.today()
    with get_session() as session:
        open_orders = session.scalar(select(func.count()).select_from(Order).where(Order.status == "Placed")) or 0
        last_order = session.scalar(select(func.max(Order.order_date)))
    forecast = forecast_month(current.year, current.month)
    total_forecast = forecast["forecast_units"].sum()
    st.markdown('<p class="status-note">Model status: trained v3 stacking ensemble is ready for planning.</p>', unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    a.metric("This month forecast", f"{total_forecast:,.0f} units")
    b.metric("Model SKUs", len(bundle["skus"]))
    c.metric("Open orders", open_orders)
    d.metric("Last order", str(last_order or "None"))
    st.subheader("Current-month forecast")
    chart = forecast.groupby("sku_id", as_index=False)["forecast_units"].sum().rename(columns={"forecast_units": "units"})
    st.bar_chart(chart.set_index("sku_id"), color="#167d7f")
    st.subheader("Model validation")
    metrics = pd.DataFrame(bundle["metrics"]).T.reset_index().rename(columns={"index": "sku_id"})
    st.dataframe(metrics, use_container_width=True, hide_index=True)
except Exception as exc:
    st.error(f"The dashboard could not load: {exc}")
    st.info("Run `python train_model.py` once before starting Streamlit.")
