import dropbox
from datetime import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from app import app, db, CalendarEntry
import pandas as pd
import os

# === STEP 1: Your Dropbox Access Token ===
ACCESS_TOKEN = 'sl.u.AFrimaMeCophD-173gAGwDpzSPXcr4oq_ThecfVNZjc5LRS8HtaFD7YN3iV9piBG3zCnlQtWPQpz1TR8GXOMV2VJCvUlCQZxDu1xR46ULbCDzEKEGp0n73xU-oceAZ8kPOaXW90ZCNWqNmZ1uJr0Mjpb5kotVNugAe-jiNUmFaY8jMiM-PdqNMtV3ZjzVSrCD5Ptg4vmqXazqE5Nm3Xqj9Yvl2yDquszJqHbIuLGO1QK4EMURVTSfJnQG8-LCClLeukvAHEN7KhVW8HGzL6l-90YBJtdOQArYChliTi-KRNK1Y429CxPfIP07shKnZ9_9rpTDikxcF8-9lHqfrs8OlAP5Zxw5O9mNe2Ne_hGcSz4ihZW5m5UBV8CG1rOacGe-NrBJyIuIZERhLkWS6xzO4da1eLRvYozue2bJVYJGsfnHAo5yi_DPXNtEDIPHlLFScdVm7hg066dh5BtmzDBrYh_guLpVvCzs-ooNRE6SowAYBnu6nDmerZB7GYmsDDY1-fOF29qYIXHn7V0dtQ67QZuw-cEbHdVb0lE5sNFGQ3aDSRy0vPc36QVzmdctMObaU0y-vEa15ItqcERaa7-SucDUrFajUv9GsuIbPexf2v2_ZC3akEmmt4Ua_qQFr08mvDzz6y4vfECvzjGnSiGwSVteOjAZfx1TWsEa8GhMq0i8fxMhRleTFF6v_vno17mvm8OOO_QwpQRXWtdeymC2esy7QaNlq4Cd9y6JD8C2PMcUWXCOLojV6vRmp2HSFTMs4fQ1R_VPeH0-R5Jg_VZ06Au4nuyVMlJTzr5FIDKvYqVNc1Dk8u01KOpr7CUBtq5VdpJwV4aAXQAQ83e-yv6SmFlGNgBNvLeHAn-6KtkyTsEvAdwAASOj3OyhfSk5mfoEtt9ltpph08FNMuwpDbI0vm6DfU3zfZnj_-Wgczfg_aWd1r7Xzp7vzL4s1YMv6AmrJiePb61s4QHRz0Ra81J6y75toF9NAXiuRc_MkTqLLz2gFXz0X2G9wDZsfkixM36ep6YFDfNl7mfz4PA6CQ5tqn58eQQT8FUNEUb-CJmF_sf0rDFecs4IQOtiJvFVY-jaBzsu3qy-4KXmmwiFhIIiHN6eHlXxvIGzbES8CA9cn3NU-gJ16P3xXmuCAtQMFE_x1_P44UvD3lBvZit0hPhAqc_JVPF4NCIxBWw4a7ljNHk-LhGc6svHsqLVFdZwBO2tQiuufzkLlCsOyzVmiaYqeod49d7JfxlF5H07pcJGZnDEena7eo1zJLLpDnKzndj9gaj0d35bwr35QASgrLU-Sjy4y9-YyFSHBvzpt7wRfYKMA'  # Replace this with your token

# === STEP 2: Export data to Excel (same format as /export_all) ===
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
        workbook = writer.book
        worksheet = writer.sheets['All Data']
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        worksheet.set_column('A:C', 40, wrap_format)
    output.seek(0)
    return output

# === STEP 3: Upload file to Dropbox ===
def upload_to_dropbox(file_content, filename):
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    dropbox_path = f"/CalendarBackups/{filename}"
    dbx.files_upload(file_content.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
    print(f"✅ Uploaded to Dropbox as {dropbox_path}")

# === STEP 4: Main function to run ===
if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"calendar_backup_{today}.xlsx"
    print("🔄 Generating backup...")
    with app.app_context():
        excel_data = generate_excel()
        upload_to_dropbox(excel_data, filename)
