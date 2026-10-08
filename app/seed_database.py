"""Command-line entry point for creating and seeding the database."""

from app.db.seed import seed_database, validate_seed_costs


if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully.")
    for sku_id, cost in validate_seed_costs().items():
        print(f"{sku_id}: ${cost:.2f}")
