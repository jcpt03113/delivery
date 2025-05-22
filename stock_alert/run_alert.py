from db_access import get_upcoming_deliveries
from stock_loader import load_stock_data
from matcher import find_stock_shortages
from notifier import send_sms_alert

def main():
    print("📦 Loading delivery data...")
    deliveries = get_upcoming_deliveries()

    print("📊 Loading stock data...")
    stock_data = load_stock_data()

    print("🔍 Matching delivery to stock...")
    shortages = find_stock_shortages(deliveries, stock_data)

    print("📤 Sending alerts...")
    send_sms_alert(shortages)

if __name__ == '__main__':
    main()
