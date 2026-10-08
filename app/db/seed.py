"""Seed the database with the supplied illustrative planning data."""

from decimal import Decimal

from sqlalchemy import select

from app.db.database import get_session, init_database
from app.db.models import BOM, Material, SKU, Stock


SKU_DATA = {
    "MBA13": "13-inch laptop, 8GB RAM, 256GB SSD",
    "MBP14": "14-inch laptop, 16GB RAM, 512GB SSD",
    "MBP16": "16-inch Pro laptop, 16GB RAM, 512GB SSD",
    "MBA15": "14-inch entry laptop, 8GB RAM, 256GB SSD",
}

MATERIAL_DATA = [
    ("M01", "Display panel 13in", "pcs", 70, 500, 21, 800),
    ("M02", "Display panel 14in", "pcs", 85, 500, 21, 600),
    ("M03", "Display panel 16in", "pcs", 120, 500, 25, 400),
    ("M04", "Battery 45Wh", "pcs", 28, 1000, 14, 1200),
    ("M05", "Battery 55Wh", "pcs", 34, 1000, 14, 800),
    ("M06", "Battery 80Wh", "pcs", 48, 1000, 14, 600),
    ("M07", "SoC base", "pcs", 110, 1000, 45, 1500),
    ("M08", "SoC pro", "pcs", 190, 500, 45, 500),
    ("M09", "RAM 8GB", "pcs", 22, 1000, 30, 1500),
    ("M10", "RAM 16GB", "pcs", 42, 1000, 30, 1000),
    ("M11", "SSD 256GB", "pcs", 24, 1000, 28, 1500),
    ("M12", "SSD 512GB", "pcs", 40, 1000, 28, 1000),
    ("M13", "Aluminium chassis material", "kg", 9, 500, 10, 3000),
    ("M14", "Keyboard assembly", "pcs", 18, 1000, 20, 1800),
    ("M15", "Trackpad module", "pcs", 12, 1000, 20, 1800),
    ("M16", "Logic board PCB", "pcs", 35, 1000, 30, 1600),
    ("M17", "Cooling module", "pcs", 9, 1000, 14, 1600),
    ("M18", "Speaker and mic set", "pcs", 8, 1000, 14, 1800),
    ("M19", "Packaging kit", "pcs", 4, 2000, 7, 3000),
]

BOM_DATA = {
    "MBA13": {"M01": 1, "M04": 1, "M07": 1, "M09": 1, "M11": 1, "M13": 1.0, "M14": 1, "M15": 1, "M16": 1, "M17": 1, "M18": 1, "M19": 1},
    "MBP14": {"M02": 1, "M05": 1, "M07": 1, "M10": 1, "M12": 1, "M13": 1.2, "M14": 1, "M15": 1, "M16": 1, "M17": 1, "M18": 1, "M19": 1},
    "MBP16": {"M03": 1, "M06": 1, "M08": 1, "M10": 1, "M12": 1, "M13": 1.6, "M14": 1, "M15": 1, "M16": 1, "M17": 2, "M18": 1, "M19": 1},
    "MBA15": {"M02": 1, "M05": 1, "M07": 1, "M09": 1, "M11": 1, "M13": 1.2, "M14": 1, "M15": 1, "M16": 1, "M17": 1, "M18": 1, "M19": 1},
}


def seed_database() -> None:
    """Create the schema and insert seed rows only when the database is empty."""
    init_database()
    with get_session() as session:
        if session.scalar(select(SKU.id).limit(1)) is not None:
            return

        sku_rows = {sku_id: SKU(sku_id=sku_id, name=name) for sku_id, name in SKU_DATA.items()}
        session.add_all(list(sku_rows.values()))

        material_rows = {}
        for material_id, name, unit, cost, moq, lead_time, opening_stock in MATERIAL_DATA:
            material = Material(
                material_id=material_id,
                name=name,
                unit=unit,
                unit_cost=Decimal(str(cost)),
                moq=Decimal(str(moq)),
                lead_time_days=lead_time,
            )
            material_rows[material_id] = material
            session.add(material)
            session.add(Stock(material=material, quantity=Decimal(str(opening_stock))))

        session.flush()
        for sku_id, material_quantities in BOM_DATA.items():
            for material_id, quantity in material_quantities.items():
                session.add(
                    BOM(
                        sku=sku_rows[sku_id],
                        material=material_rows[material_id],
                        quantity_per_unit=Decimal(str(quantity)),
                    )
                )
        session.commit()


def validate_seed_costs() -> dict[str, Decimal]:
    """Calculate the material cost per laptop from the seeded BOM."""
    init_database()
    with get_session() as session:
        materials = {row.material_id: row for row in session.scalars(select(Material)).all()}
        skus = {row.sku_id: row for row in session.scalars(select(SKU)).all()}
        costs = {}
        for sku_id, sku in skus.items():
            rows = session.scalars(select(BOM).where(BOM.sku_id == sku.id)).all()
            costs[sku_id] = sum((materials[row.material.material_id].unit_cost * row.quantity_per_unit for row in rows), Decimal("0"))
        return costs


if __name__ == "__main__":
    seed_database()
    for sku_id, cost in validate_seed_costs().items():
        print(f"{sku_id}: ${cost:.2f}")
