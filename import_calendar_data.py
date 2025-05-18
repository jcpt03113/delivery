import os
import pandas as pd
from app import db, CalendarEntry, app
from datetime import datetime

FILE_PATH = "calendar_entry_template.csv"

def normalize_date(value):
    """Convert any datetime or string with time to YYYY-MM-DD format."""
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    except:
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            return ""

with app.app_context():
    print("DB URL:", app.config['SQLALCHEMY_DATABASE_URI'])

    df = pd.read_csv(FILE_PATH).fillna("")

    added = 0
    for _, row in df.iterrows():
        raw_date = str(row.get("date", "")).strip()
        raw_expected = str(row.get("expected_date", "")).strip()

        # Normalize both dates
        norm_date = normalize_date(raw_date)
        norm_expected = normalize_date(raw_expected)

        # Fallback rule
        if not norm_expected:
            norm_expected = norm_date

        if not norm_date:
            continue  # skip invalid entry

        entry = CalendarEntry(
            date=norm_date,
            expected_date=norm_expected,
            note=row.get("note", ""),
            details=row.get("details", ""),
            text_color=row.get("text_color", "#000000"),
            is_closed=str(row.get("is_closed", "")).strip().lower() == "true"
        )
        db.session.add(entry)
        added += 1

    db.session.commit()
    print(f"✅ Data import completed. {added} entries added.")
