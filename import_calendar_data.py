import os
import pandas as pd
from datetime import datetime, timezone
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
FILE_PATH = "calendar_entry_template.csv"

with app.app_context():
    df = pd.read_csv(FILE_PATH).fillna("")
    now = datetime.now(timezone.utc)
    added, updated = 0, 0

    # STEP 1: Load existing notes into dict for fast lookup
    existing_entries = CalendarEntry.query.with_entities(
        CalendarEntry.id, CalendarEntry.note
    ).all()
    existing_notes = {e.note.strip().lower(): e.id for e in existing_entries}

    # STEP 2: Loop through CSV rows
    for _, row in df.iterrows():
        note = str(row.get("note", "")).strip()
        if not note:
            continue  # Skip empty notes

        note_key = note.lower()
        date_val = str(row.get("date", "")).strip()
        expected_val = str(row.get("expected_date", "")).strip() or date_val
        color = str(row.get("text_color", "#000000")).strip() or "#000000"
        details = str(row.get("details", "")).strip()
        closed = str(row.get("is_closed", "")).strip().lower() in ['true', 'yes', '1']

        if note_key in existing_notes:
            # Update existing entry
            existing_entry = CalendarEntry.query.get(existing_notes[note_key])
            existing_entry.date = date_val
            existing_entry.expected_date = expected_val
            existing_entry.details = details
            existing_entry.text_color = color
            existing_entry.is_closed = closed
            existing_entry.timestamp = now
            updated += 1
        else:
            # Insert new entry
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
