import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from app import app, db, CalendarEntry
import pandas as pd
import dropbox

# Load from GitHub Actions environment
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

def generate_excel():
    entries = CalendarEntry.query.order_by(CalendarEntry.date).all()
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
        wrap_format = writer.book.add_format({'text_wrap': True, 'valign': 'top'})
        writer.sheets['All Data'].set_column('A:C', 40, wrap_format)
    output.seek(0)
    return output

def upload_to_dropbox(file_content, filename):
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    path = f"/CalendarBackups/{filename}"
    dbx.files_upload(file_content.read(), path, mode=dropbox.files.WriteMode.overwrite)
    print(f"✅ Uploaded to Dropbox as {path}")

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"calendar_backup_{today}.xlsx"
    print("🔄 Generating backup...")
    with app.app_context():
        excel_data = generate_excel()
        upload_to_dropbox(excel_data, filename)
