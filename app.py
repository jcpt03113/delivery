from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Setup database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the table/model
class CalendarEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_color = db.Column(db.String(20), default="#000000")
    date = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=False)  # HTML note from Quill
    details = db.Column(db.Text, default="")
    address = db.Column(db.String(255), default="")
    phone = db.Column(db.String(50), default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    entries = CalendarEntry.query.order_by(CalendarEntry.date).all()
    calendar_data = {}
    for entry in entries:
        if entry.date in calendar_data:
            calendar_data[entry.date].append(entry)
        else:
            calendar_data[entry.date] = [entry]
    return render_template('calendar.html', calendar_data=calendar_data)

@app.route('/calendar')
def full_calendar():
    return render_template('fullcalendar.html')

@app.route('/events')
def events():
    entries = CalendarEntry.query.all()
    events = []
    for entry in entries:
        events.append({
            'id': entry.id,
            'title': '',  # We'll use HTML inside description
            'start': entry.date,
            'description': entry.note,  # already HTML
            'details': entry.details,
            'address': entry.address,
            'phone': entry.phone
        })
    return jsonify(events)

@app.route('/add_from_calendar', methods=['POST'])
def add_from_calendar():
    date = request.form.get('date')
    note = request.form.get('note')  # HTML
    details = request.form.get('details')
    address = request.form.get('address')
    phone = request.form.get('phone')

    new_entry = CalendarEntry(
        date=date,
        note=note,
        details=details,
        address=address,
        phone=phone
    )
    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for('full_calendar'))

@app.route('/edit_from_calendar/<int:id>', methods=['POST'])
def edit_from_calendar(id):
    entry = CalendarEntry.query.get_or_404(id)
    entry.date = request.form.get('date')
    entry.note = request.form.get('note')  # HTML
    entry.details = request.form.get('details')
    entry.address = request.form.get('address')
    entry.phone = request.form.get('phone')
    db.session.commit()
    return redirect(url_for('full_calendar'))

if __name__ == '__main__':
    app.run(debug=True)
