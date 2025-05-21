import os
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Flask and DB setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") + "?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CalendarEntry model
class CalendarEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_color = db.Column(db.String(20), default="#000000")
    date = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_closed = db.Column(db.Boolean, default=False)
    expected_date = db.Column(db.String(20))

def check_bad_recent_entries():
    now = datetime.utcnow()
    two_days_ago = now - timedelta(days=2)

    recent = CalendarEntry.query.filter(CalendarEntry.timestamp >= two_days_ago).all()
    bad_entries = []

    for e in recent:
        expected = e.expected_date
        if not expected or not isinstance(expected, str) or not expected.strip().startswith("20"):
            bad_entries.append({
                "ID": e.id,
                "NOTE": e.note,
                "DATE": e.date,
                "EXPECTED_DATE": e.expected_date,
                "TIMESTAMP": e.timestamp.isoformat()
            })

    df = pd.DataFrame(bad_entries)
    filename = f"bad_entries_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ Exported {len(bad_entries)} bad entries to {filename}")

if __name__ == '__main__':
    with app.app_context():
        check_bad_recent_entries()
