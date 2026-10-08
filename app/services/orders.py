"""Order persistence and stock-receipt operations."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.db.database import get_session
from app.db.models import Material, Order, OrderItem, Stock


def save_order(planned_month: date, plan_df, forecasts: dict[str, float]) -> int:
    """Save the edited plan as a placed order and return its database ID."""
    with get_session() as session:
        order = Order(planned_month=planned_month, status="Placed", total_cost=Decimal("0"))
        session.add(order)
        session.flush()
        total = Decimal("0")
        for row in plan_df.to_dict("records"):
            quantity = Decimal(str(row["order_qty"]))
            suggested = Decimal(str(row["suggested_qty"]))
            if quantity <= 0:
                continue
            material = session.scalar(select(Material).where(Material.material_id == row["material_id"]))
            line_total = quantity * material.unit_cost
            session.add(OrderItem(order_id=order.id, material_id=material.id, suggested_quantity=suggested, final_quantity=quantity, was_edited=int(quantity != suggested), unit_cost=material.unit_cost, line_total=line_total))
            total += line_total
        order.total_cost = total
        session.commit()
        return order.id


def list_orders():
    """Return all orders with their line items for the history page."""
    with get_session() as session:
        return session.scalars(select(Order).order_by(Order.order_date.desc(), Order.id.desc())).all()


def update_order_status(order_id: int, status: str) -> None:
    """Update an order status and add received quantities to current stock once."""
    with get_session() as session:
        order = session.get(Order, order_id)
        if not order or order.status == status:
            return
        if status == "Received" and order.status != "Received":
            for item in order.items:
                stock = session.scalar(select(Stock).where(Stock.material_id == item.material_id))
                stock.quantity += item.final_quantity
        order.status = status
        session.commit()
