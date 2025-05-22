import pandas as pd
from config import STOCK_FILE_PATH

def load_stock_data():
    try:
        df = pd.read_excel(STOCK_FILE_PATH)
    except Exception as e:
        print(f"❌ Error loading stock file: {e}")
        return {}

    # 🔁 Adjusted for 'Item Code' column instead of 'Product Code'
    stock_dict = {}

    for _, row in df.iterrows():
        code = str(row.get('Item Code', '')).strip().upper()
        qty = row.get('Qty', 0)

        if code:
            stock_dict[code] = qty

    return stock_dict
