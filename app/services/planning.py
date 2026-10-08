"""Raw-material requirement, MOQ, safety-stock, and lead-time calculations."""

from calendar import monthrange
from datetime import date
from decimal import Decimal
from math import ceil

import pandas as pd
from sqlalchemy import select

from app.db.database import get_session
from app.db.models import BOM, Material, SKU, Stock


def calculate_plan(forecasts: dict[str, float], year: int, month: int, safety_rate: float = 0.10) -> pd.DataFrame:
    """Calculate material requirements and MOQ-rounded order suggestions."""
    with get_session() as session:
        skus = {row.sku_id: row for row in session.scalars(select(SKU)).all()}
        materials = {row.id: row for row in session.scalars(select(Material)).all()}
        stocks = {row.material_id: row.quantity for row in session.scalars(select(Stock)).all()}
        rows = []
        days_left = max(0, (date(year, month, monthrange(year, month)[1]) - date.today()).days)
        for material in materials.values():
            required = Decimal("0")
            for sku_id, units in forecasts.items():
                if sku_id not in skus:
                    continue
                bom = session.scalar(select(BOM).where(BOM.sku_id == skus[sku_id].id, BOM.material_id == material.id))
                if bom:
                    required += Decimal(str(units)) * bom.quantity_per_unit
            safety = required * Decimal(str(safety_rate))
            raw_suggested = max(Decimal("0"), required + safety - stocks.get(material.id, Decimal("0")))
            if raw_suggested > 0:
                suggested = Decimal(str(ceil(float(raw_suggested / material.moq)))) * material.moq
            else:
                suggested = Decimal("0")
            rows.append({
                "material_id": material.material_id, "material": material.name, "unit": material.unit,
                "required_qty": float(required), "safety_stock": float(safety), "current_stock": float(stocks.get(material.id, 0)),
                "suggested_qty": float(suggested), "order_qty": float(suggested), "unit_cost": float(material.unit_cost),
                "moq": float(material.moq), "lead_time_days": material.lead_time_days,
                "lead_time_warning": material.lead_time_days > days_left,
            })
        return pd.DataFrame(rows)
