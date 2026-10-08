# Production Planning Optimisation — Stage 2

Stage 2 adds the SQLite database, SQLAlchemy models, and first-run seed data.

## Database tables

| Table | Purpose |
|---|---|
| `skus` | Laptop SKU IDs and descriptions. |
| `materials` | Material name, unit, cost, MOQ, and lead time. |
| `bom` | Quantity of each material required for one SKU. |
| `stock` | Current stock by material. |
| `forecasts` | Monthly forecast values used for planning. |
| `orders` | Confirmed order header, status, and total cost. |
| `order_items` | Material lines, suggested/final quantities, edits, and costs. |

## Seed data used

The database uses the confirmed mapping:

- `SKU_B` → `MBP14`
- `SKU_C` → `MBP16`
- `SKU_D` → `MBA15`

The user-facing descriptions retain the supplied BOM descriptions. The supplied material costs reproduce exactly:

```text
MBA13: $349.00
MBP14: $407.80
MBP16: $549.40
MBA15: $371.80
```

## Test from PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.seed_database
```

Expected output:

```text
Database seeded successfully.
MBA13: $349.00
MBP14: $407.80
MBP16: $549.40
MBA15: $371.80
```

The Streamlit app also creates and seeds the database automatically on first run. Existing rows are not overwritten.
