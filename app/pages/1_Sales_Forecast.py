"""Sales Forecast page."""

from datetime import date

import pandas as pd
import streamlit as st

from app.services.forecast import forecast_month

st.title("Sales Forecast")
st.write("Forecast monthly demand recursively from the trained v3 positive-ridge stacking model.")
col1, col2, col3, col4 = st.columns(4)
year = col1.number_input("Year", min_value=2022, max_value=2100, value=date.today().year)
month = col2.number_input("Month", min_value=1, max_value=12, value=date.today().month)
promo = col3.toggle("Promotion active", value=False)
stockout = col4.toggle("Stockout active", value=False)
if st.button("Predict", type="primary"):
    st.session_state.forecast_daily = forecast_month(int(year), int(month), promo, stockout)
    st.session_state.forecast_month = {sku: float(total) for sku, total in st.session_state.forecast_daily.groupby("sku_id")["forecast_units"].sum().items()}
if "forecast_daily" in st.session_state:
    daily = st.session_state.forecast_daily
    monthly = daily.groupby("sku_id", as_index=False)["forecast_units"].sum().rename(columns={"forecast_units": "forecast_units"})
    overrides = {}
    st.subheader("Monthly forecast")
    for _, row in monthly.iterrows():
        overrides[row["sku_id"]] = st.number_input(f"{row['sku_id']} units", min_value=0.0, value=float(row["forecast_units"]), step=1.0, key=f"override_{row['sku_id']}")
    st.session_state.forecast_month = overrides
    st.dataframe(monthly, use_container_width=True, hide_index=True)
    st.subheader("Daily forecast")
    st.line_chart(daily.pivot(index="date", columns="sku_id", values="forecast_units"))
    st.success("Forecast saved in this session. Open Raw Material Planning to use it.")
