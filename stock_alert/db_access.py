from sqlalchemy import create_engine, text
from config import DAYS_AHEAD

# ✅ Your actual PostgreSQL database URL from Render
DATABASE_URL = 'postgresql://anzhome:HKBKcJVneu9uwVkDJ6QB2IBMGBj4OeVz@dpg-d081a7ngi27c738206vg-a.oregon-postgres.render.com/anzdelivery'

query = text(f"""
    SELECT note, details, expected_date
    FROM (
        SELECT * FROM calendar_entry
        WHERE expected_date IS NOT NULL
          AND TRIM(expected_date) <> ''
    ) AS filtered
    WHERE expected_date::date >= CURRENT_DATE
      AND expected_date::date <= CURRENT_DATE + interval '{DAYS_AHEAD} days'
""")


def get_upcoming_deliveries():
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()

    query = text(f"""
        SELECT note, details, expected_date
    FROM (
        SELECT * FROM calendar_entry
        WHERE expected_date IS NOT NULL
          AND TRIM(expected_date) <> ''
    ) AS filtered
    WHERE expected_date::date >= CURRENT_DATE
      AND expected_date::date <= CURRENT_DATE + interval '{DAYS_AHEAD} days'
    """)

    results = conn.execute(query).fetchall()
    conn.close()

    deliveries = []
    for row in results:
        deliveries.append({
            'note': row.note,
            'details': row.details,
            'expected_date': row.expected_date
        })

    return deliveries
