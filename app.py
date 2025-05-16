from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from bs4 import BeautifulSoup
from io import BytesIO
import pandas as pd
import os

from dotenv import load_dotenv
load_dotenv()
print("DB URL:", os.getenv("DATABASE_URL"))

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

# Enforce ?sslmode=require and engine SSL options
raw_db_url = os.getenv("DATABASE_URL", "")
if raw_db_url and 'sslmode=' not in raw_db_url:
    raw_db_url += '?sslmode=require'

app.config['SQLALCHEMY_DATABASE_URI'] = raw_db_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"sslmode": "require"}
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

print("Connected to:", app.config['SQLALCHEMY_DATABASE_URI'])


from datetime import timedelta

app.permanent_session_lifetime = timedelta(minutes=20)



# Login manager setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Calendar model
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

# Login system with multiple hardcoded users
class User(UserMixin):
    def __init__(self, id, password):
        self.id = id
        self.name = id
        self.password = password

# Define users here
users = {
    'admin': User(id='admin', password='anzhome1388'),
    'showroom': User(id='showroom', password='anzdelivery')
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)
# ====== ROUTES ======

@app.route('/')
@login_required
def full_calendar():
    return render_template('fullcalendar.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users.get(username)
        if user and password == user.password:
            login_user(user)
            return redirect(url_for('full_calendar'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_from_calendar', methods=['POST'])
def add_from_calendar():
    date_input = request.form.get('date')
    expected_input = request.form.get('expected_date') or date_input

    new_entry = CalendarEntry(
        date=date_input,
        expected_date=expected_input,
        note=request.form.get('note'),
        details=request.form.get('details'),
        text_color=request.form.get('text_color', '#000000'),
        is_closed=('is_closed' in request.form)
    )
    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for('full_calendar'))


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

@app.route('/edit_from_calendar/<int:id>', methods=['POST', 'DELETE'])
def edit_from_calendar(id):
    entry = CalendarEntry.query.get_or_404(id)

    if request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return '', 204

    updated_date = request.form.get('expected_date')  # always use expected_date as new source of truth

    entry.expected_date = updated_date
    entry.date = updated_date  # sync the date
    entry.note = request.form.get('note')
    entry.details = request.form.get('details')
    entry.text_color = request.form.get('text_color', '#000000')
    entry.is_closed = 'is_closed' in request.form

    db.session.commit()
    return redirect(url_for('full_calendar'))








    # Existing POST edit logic remains unchanged...


@app.route('/delete_from_calendar/<int:id>', methods=['POST'])
def delete_from_calendar(id):
    entry = CalendarEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('full_calendar'))

@app.route("/search_events")
def search_events():
    keyword = request.args.get("q", "").lower().strip()
    start_date = request.args.get("start")
    end_date = request.args.get("end")

    results = []

    # Convert strings to actual date objects
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
    except ValueError:
        start_date_obj = end_date_obj = None  # fail-safe

    entries = CalendarEntry.query.all()

    for entry in entries:
        note = (entry.note or "").lower()
        details = (entry.details or "").lower()
        if keyword not in note and keyword not in details:
            continue

        # pick the date to compare
        date_str = entry.expected_date or entry.date
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            continue  # skip bad date formats

        # Check date filters
        if start_date_obj and entry_date < start_date_obj:
            continue
        if end_date_obj and entry_date > end_date_obj:
            continue

        # Passed all filters
        results.append({
            'id': entry.id,
            'title': entry.note,
            'details': entry.details,
            'start': date_str,
            'textColor': entry.text_color
        })

    return jsonify(results)

@app.route('/export_excel/<date_str>')
def export_excel(date_str):
    entries = CalendarEntry.query.filter_by(date=date_str).all()
    if not entries:
        return "No data found for selected date", 404

    data = []
    for e in entries:
        plain_details = BeautifulSoup(e.details or "", "html.parser").get_text(separator="\n")
        data.append({
            'Note': f"[CLOSED] {e.note}" if e.is_closed else e.note,
            'Details': plain_details
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        worksheet.set_column('A:B', 40, wrap_format)

    output.seek(0)
    filename = f"calendar_export_{date_str}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/export_all')
def export_all():
    entries = CalendarEntry.query.order_by(CalendarEntry.date).all()
    if not entries:
        return "No data found", 404

    data = []
    for e in entries:
        plain_details = BeautifulSoup(e.details or "", "html.parser").get_text(separator="\n")
        data.append({
            'Date': e.date,
            'Note': f"[CLOSED] {e.note}" if e.is_closed else e.note,
            'Details': plain_details
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='All Data')
        workbook = writer.book
        worksheet = writer.sheets['All Data']
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        worksheet.set_column('A:C', 40, wrap_format)

    output.seek(0)
    return send_file(output, as_attachment=True, download_name="all_calendar_data.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/test_export')
def test_export():
    return "Test Export OK"

@app.route('/fix_expected_date_once')
def fix_expected_date_once():
    entries = CalendarEntry.query.filter(
        (CalendarEntry.expected_date == None) | (CalendarEntry.expected_date == '')
    ).all()

    count = 0
    for entry in entries:
        entry.expected_date = entry.date
        count += 1

    db.session.commit()
    return f"✅ Fixed {count} entries where expected_date was blank."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
