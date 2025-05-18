import pandas as pd

# This matches your CalendarEntry model fields
data = [{
    "date": "2024-01-01",
    "expected_date": "2024-01-01",
    "note": "Sample Note",
    "details": "<p>Sample details (rich text HTML)</p>",
    "text_color": "#000000",
    "is_closed": False,
    "timestamp": "2024-01-01 10:00:00"
}]

df = pd.DataFrame(data)
df.to_csv("calendar_entry_template.csv", index=False)
print("✅ Template file created: calendar_entry_template.csv")
