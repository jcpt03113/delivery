import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load environment
load_dotenv()

# Flask app + DB setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") + "?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DB model
class CalendarEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_color = db.Column(db.String(20), default="#000000")
    date = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_closed = db.Column(db.Boolean, default=False)
    expected_date = db.Column(db.String(20))

# === Bulk Import Logic ===
FILE_PATH = "import_calendar_data.csv"

with app.app_context():
    df = pd.read_csv(FILE_PATH).fillna("")

    added = 0
    updated = 0
    now = datetime.utcnow()

    for _, row in df.iterrows():
        note = str(row.get("note", "")).strip()
        if not note:
            continue  # Skip if no NOTE value

        existing = CalendarEntry.query.filter_by(note=note).first()

        # Fallback for missing expected date
        date_val = str(row.get("date", "")).strip()
        expected_val = str(row.get("expected_date", "")).strip() or date_val
        color = str(row.get("text_color", "#000000")).strip() or "#000000"
        details = str(row.get("details", "")).strip()
        closed = str(row.get("is_closed", "")).strip().lower() in ['true', 'yes', '1']

        if existing:
            existing.date = date_val
            existing.expected_date = expected_val
            existing.details = details
            existing.text_color = color
            existing.is_closed = closed
            existing.timestamp = now
            updated += 1
        else:
            new_entry = CalendarEntry(
                date=date_val,
                expected_date=expected_val,
                note=note,
                details=details,
                text_color=color,
                is_closed=closed,
                timestamp=now
            )
            db.session.add(new_entry)
            added += 1

    db.session.commit()
    print(f"✅ Import complete. {added} added, {updated} updated.")
