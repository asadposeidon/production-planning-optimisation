"""Order History page."""

import streamlit as st

from app.services.orders import list_orders, update_order_status

st.title("Order History")
orders = list_orders()
if not orders:
    st.info("No orders have been placed yet.")
else:
    rows = [{"Order ID": o.id, "Order date": o.order_date, "Planned month": o.planned_month, "Status": o.status, "Total cost": float(o.total_cost)} for o in orders]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    selected = st.selectbox("Select order", [o.id for o in orders])
    order = next(o for o in orders if o.id == selected)
    st.dataframe([{"Material": item.material.material_id, "Name": item.material.name, "Suggested": float(item.suggested_quantity), "Final": float(item.final_quantity), "Edited": bool(item.was_edited), "Line total": float(item.line_total)} for item in order.items], use_container_width=True, hide_index=True)
    status = st.selectbox("Update status", ["Placed", "Shipped", "Received", "Cancelled"], index=["Placed", "Shipped", "Received", "Cancelled"].index(order.status) if order.status in ["Placed", "Shipped", "Received", "Cancelled"] else 0)
    if st.button("Save status"):
        update_order_status(order.id, status)
        st.success("Order status updated.")
        st.rerun()
