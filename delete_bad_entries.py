import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import re

# Load .env
load_dotenv()

# Setup Flask + DB
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

def delete_bad_entries():
    bad_entries = CalendarEntry.query.filter(
        (CalendarEntry.expected_date == None) |
        (CalendarEntry.expected_date == '') |
        (~CalendarEntry.expected_date.op("~")(r"^\d{4}-\d{2}-\d{2}$"))
    ).all()

    count = len(bad_entries)
    for e in bad_entries:
        db.session.delete(e)

    db.session.commit()
    print(f"🗑️ Deleted {count} bad entries with broken or missing expected_date.")

if __name__ == '__main__':
    with app.app_context():
        delete_bad_entries()
