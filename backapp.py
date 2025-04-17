from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class CalendarEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_color = db.Column(db.String(20), default="#000000")
    date = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_closed = db.Column(db.Boolean, default=False)
    expected_date = db.Column(db.String(20))  # ISO date format

with app.app_context():
    db.create_all()

@app.route('/')
def full_calendar():
    return render_template('fullcalendar.html')

@app.route('/events')
def events():
    entries = CalendarEntry.query.all()
    events = []
    for entry in entries:
        title = f"[CLOSED] {entry.note}" if entry.is_closed else entry.note
        events.append({
            'id': entry.id,
            'title': title,
            'start': entry.expected_date if entry.expected_date else entry.date,
            'textColor': entry.text_color,
            'extendedProps': {
                'details': entry.details,
                'original_date': entry.date,
                'expected_date': entry.expected_date,
                'is_closed': entry.is_closed
            }
        })
    return jsonify(events)

@app.route('/add_from_calendar', methods=['POST'])
def add_from_calendar():
    new_entry = CalendarEntry(
        date=request.form.get('date'),
        note=request.form.get('note'),
        details=request.form.get('details'),
        text_color=request.form.get('text_color', '#000000'),
        is_closed=('is_closed' in request.form),
        expected_date=request.form.get('expected_date')
    )
    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for('full_calendar'))

@app.route('/edit_from_calendar/<int:id>', methods=['POST'])
def edit_from_calendar(id):
    entry = CalendarEntry.query.get_or_404(id)
    entry.date = request.form.get('date')
    entry.note = request.form.get('note')
    entry.details = request.form.get('details')
    entry.text_color = request.form.get('text_color', '#000000')
    entry.is_closed = 'is_closed' in request.form
    entry.expected_date = request.form.get('expected_date')
    db.session.commit()
    return redirect(url_for('full_calendar'))

@app.route('/delete_from_calendar/<int:id>', methods=['POST'])
def delete_from_calendar(id):
    entry = CalendarEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('full_calendar'))

@app.route("/search_events")
def search_events():
    keyword = request.args.get("q", "").lower().strip()
    if not keyword:
        return jsonify([])

    matches = []
    entries = CalendarEntry.query.all()
    for entry in entries:
        note = (entry.note or "").lower()
        details = (entry.details or "").lower()
        if keyword in note or keyword in details:
            matches.append({
                'id': entry.id,
                'title': entry.note,
                'details': entry.details,
                'start': entry.date,
                'textColor': entry.text_color
            })
    return jsonify(matches)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
