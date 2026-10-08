"""SQLAlchemy database models for production planning."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Provide the base class shared by all database tables."""


class SKU(Base):
    """Store one laptop SKU and its display name."""

    __tablename__ = "skus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    bom_rows: Mapped[list["BOM"]] = relationship(back_populates="sku", cascade="all, delete-orphan")


class Material(Base):
    """Store material master data used for planning and ordering."""

    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    moq: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    bom_rows: Mapped[list["BOM"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    stock_rows: Mapped[list["Stock"]] = relationship(back_populates="material", cascade="all, delete-orphan")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="material")


class BOM(Base):
    """Store the quantity of one material needed for one laptop SKU."""

    __tablename__ = "bom"
    __table_args__ = (UniqueConstraint("sku_id", "material_id", name="uq_bom_sku_material"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku_id: Mapped[int] = mapped_column(ForeignKey("skus.id"), nullable=False)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False)
    quantity_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)

    sku: Mapped[SKU] = relationship(back_populates="bom_rows")
    material: Mapped[Material] = relationship(back_populates="bom_rows")


class Stock(Base):
    """Store the current stock quantity for each material."""

    __tablename__ = "stock"
    __table_args__ = (UniqueConstraint("material_id", name="uq_stock_material"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    material: Mapped[Material] = relationship(back_populates="stock_rows")


class Forecast(Base):
    """Store a monthly forecast used for a planning decision."""

    __tablename__ = "forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    forecast_month: Mapped[date] = mapped_column(Date, nullable=False)
    sku_id: Mapped[int] = mapped_column(ForeignKey("skus.id"), nullable=False)
    forecast_units: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    scenario: Mapped[str] = mapped_column(String(30), default="P50", nullable=False)
    is_manual_override: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Order(Base):
    """Store one confirmed material order."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    planned_month: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Placed", nullable=False)
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Store one material line inside a confirmed order."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), nullable=False)
    suggested_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    final_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    was_edited: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")
    material: Mapped[Material] = relationship(back_populates="order_items")
