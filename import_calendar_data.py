import os
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup Flask app and DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") + "?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Calendar model
class CalendarEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_color = db.Column(db.String(20), default="#000000")
    date = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_closed = db.Column(db.Boolean, default=False)
    expected_date = db.Column(db.String(20))  # ISO format (yyyy-mm-dd)

# CSV file location
FILE_PATH = 'calendar_entry_template.csv'

with app.app_context():
    print("DB URL:", app.config['SQLALCHEMY_DATABASE_URI'])

    df = pd.read_csv(FILE_PATH)

    # Ensure required columns exist
    required = ['date', 'note', 'details']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    added = 0
    for _, row in df.iterrows():
        date = str(row['date']).strip()
        expected_date = str(row.get('expected_date', '')).strip()
        note = str(row['note']).strip()
        details = str(row.get('details', '')).strip()
        is_closed = bool(row.get('is_closed', False))
        text_color = str(row.get('text_color', '#000000')).strip()

        if not expected_date:
            expected_date = date  # Rule 1

        # Save entry
        entry = CalendarEntry(
            date=date,
            expected_date=expected_date,
            note=note,
            details=details,
            is_closed=is_closed,
            text_color=text_color
        )
        db.session.add(entry)
        added += 1

    db.session.commit()
    print(f"✅ Data import completed. {added} entries added.")
