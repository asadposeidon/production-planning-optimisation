"""Settings page for editable material and stock master data."""
import streamlit as st
from sqlalchemy import select
from app.db.database import get_session
from app.db.models import Material, SKU, Stock
from app.ui import apply_theme, page_header

st.set_page_config(page_title="Settings | Production Planning", page_icon="PP", layout="wide")
apply_theme()
page_header("Master data", "Settings", "Keep costs, MOQs, lead times, stock, and SKU descriptions aligned with the operation.")
with get_session() as session:
    materials = session.scalars(select(Material).order_by(Material.material_id)).all()
    stocks = {row.material_id: row for row in session.scalars(select(Stock)).all()}
    skus = session.scalars(select(SKU).order_by(SKU.sku_id)).all()
    material_data = [{"ID": m.material_id, "Name": m.name, "Unit": m.unit, "Unit cost": float(m.unit_cost), "MOQ": float(m.moq), "Lead time days": m.lead_time_days, "Current stock": float(stocks[m.id].quantity)} for m in materials]
    edited = st.data_editor(material_data, use_container_width=True, hide_index=True, key="materials_editor")
    if st.button("Save material settings", type="primary"):
        for row in edited:
            material = session.scalar(select(Material).where(Material.material_id == row["ID"]))
            stock = stocks[material.id]
            material.name, material.unit = row["Name"], row["Unit"]
            material.unit_cost, material.moq = row["Unit cost"], row["MOQ"]
            material.lead_time_days, stock.quantity = int(row["Lead time days"]), row["Current stock"]
        session.commit()
        st.success("Material and stock settings saved.")
st.subheader("SKU list")
st.dataframe([{"SKU": s.sku_id, "Description": s.name} for s in skus], use_container_width=True, hide_index=True)
