import sqlite3
import csv

# Connect to DB
conn = sqlite3.connect('calendar.db')
cursor = conn.cursor()

# Fetch all records
cursor.execute("SELECT * FROM calendar_entry")
rows = cursor.fetchall()

# Column names
column_names = [description[0] for description in cursor.description]

# Write to CSV
with open('calendar_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(column_names)
    writer.writerows(rows)

print("✅ Exported to calendar_export.csv")
