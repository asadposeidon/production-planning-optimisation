"""Raw Material Planning page."""
from datetime import date
import streamlit as st
from app.services.orders import save_order
from app.services.planning import calculate_plan
from app.ui import apply_theme, page_header

st.set_page_config(page_title="Material Planning | Production Planning", page_icon="PP", layout="wide")
apply_theme()
page_header("Supply planning", "Raw Material Planning", "Translate the selected forecast into an editable, MOQ-aware material order.")
forecasts = st.session_state.get("forecast_month")
if not forecasts:
    st.warning("Run Sales Forecast first, then return here to plan materials.")
    st.stop()
year, month = date.today().year, date.today().month
safety = st.number_input("Safety stock", min_value=0.0, max_value=100.0, value=10.0, step=1.0, format="%.1f") / 100
plan = calculate_plan(forecasts, year, month, safety)
plan["warning"] = plan.apply(lambda r: "Lead time risk" if r["lead_time_warning"] else ("Below required" if r["order_qty"] < r["required_qty"] else ""), axis=1)
st.subheader("Material requirements")
edited = st.data_editor(plan, use_container_width=True, hide_index=True, disabled=["material_id", "material", "unit", "required_qty", "safety_stock", "current_stock", "suggested_qty", "unit_cost", "moq", "lead_time_days", "lead_time_warning", "warning"], column_config={"order_qty": st.column_config.NumberColumn("Final order quantity", min_value=0, step=1), "warning": st.column_config.TextColumn("Review")})
total_cost = float((edited["order_qty"] * edited["unit_cost"]).sum())
left, right = st.columns([1, 3])
left.metric("Estimated order cost", f"${total_cost:,.2f}")
if (edited["order_qty"] < edited["required_qty"]).any():
    right.warning("One or more edited quantities are below the required material quantity.")
if st.button("Place order", type="primary"):
    order_id = save_order(date(year, month, 1), edited, forecasts)
    st.success(f"Order #{order_id} placed and saved.")
