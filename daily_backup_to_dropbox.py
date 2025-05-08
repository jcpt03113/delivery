import os
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from app import app, db, CalendarEntry
import pandas as pd
import dropbox

# Load from GitHub Actions environment
DROPBOX_ACCESS_TOKEN = "sl.u.AFszPo5Lq3RfcsmB7wWOM42nfU_9oObySTE6744asUFCnZ00o01IAbiWkudskDIjoMn8jBdaXhh4MTz62RWLc1ht2cyPeE6ZurRMcCDmT-HH_FUOuYpUKzXOo4_Xbhpyy3dc-vD3Iqla3dU1YNWKEZhu5b1Y60q2R-owZLoTfrZOy_LkhgrcYwWSF8_V_gGR0GdtPeScMAMwAH4l0YElys8_RuLR2v2tl9AuHhbzK0aW96YKD7dRJf47-eRT6WGkwSdSvmwxEuVeK7TUV7I7H_ozSGCvG_UDuh3p9NcDuWkULJGa8DSHvgWWNxgV6ccpwvjDYaEECFtngW3DNt2fq-2pAC18fiHSGAQE1ondSdvgvgtuWUfBzpRyiGMkl9lRp8-Ud-Am9EqkdxUjRLFgQ25W5eEE8KhhZmnwsWs2Tl7E1WLaVC2z4ImkXEjDXy-vo-8qjkpsHU0dn8itNPLNo1303tCYuUVY3fbgFcTNYmJB5a3hdkijsVOxSRuZpt3uP2jcX9Q2bG1HR0SZRwxp3FxxBbK7LVqvBFS3xl_iK-NL4abmjI1dn5uKgYWwqnt0ODsxhqNov2CmdVYyfzcHqzD_pQTSerL2xOcSXZkzeBfUHsYNqWhMiHBbg9tFYWa2oQkNhqZ-MI3FbsTH13BAJZlC3PkTrjyKe8YgkDUvT4Vn4vqTl3CSLAtQos_WIPTwKqZ0twZhpHMBkn9G9wUTxWUm58Hn7xXOJzkkl7XA3WpOoE9LpzTfX-ayAQZgmwxMfI6al19ErdVc9dAGFjVkg-ey87J18V6wIiTKEEl89nDdLuJMNfC3qx8YogyyMzkIRPT16ZlpVI0BW1BfWnZJN1oOZ6LaTYbsqhCVPr8XJ4xwdEhFxTTTppXTjdypNHY3cJcqSynKR29W3XzBgirt3nlzA4nGWN3pd2MBbTFD1j5ZV-f5AqQ02NAMZTZGblE7ULyjc60itDSQAjgX7bBGbtK2RH2vm96u7C4W4rr-IdecW6sJzKt8YcqS0GoorK6VA_0D8eA4kU_PIp3-Q5VddX0fNjMH_RXIIy4O_Kl_BsOSl9BrbwKbrH2GEYHX4PnaUhQtpU14qK8sX4fdjNjIDwgNzo5vbTONwXU_wwaM3dc8S6zzlbnM1pMOgLz0F1UmQaZCjNtw0SDXjGK9etwRJ38U9zAdgKYitC6Q1_ri87p5ZpgDJkUr3FQyhTWwQ5Dhm68xU2RAJTYEBXBysqsQVn3tNSV0KxRiTNad1k1WjEuvXaJInah3FCgAavcoNtV1t3LuPdSWnfV6zxc4DtpUNZNr"

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
