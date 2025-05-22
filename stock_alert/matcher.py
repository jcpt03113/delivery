from db_access import get_upcoming_deliveries
from stock_reader import load_stock_data
from matcher import find_stock_shortages
from notifier import send_sms_alert  # ✅ keep Twilio logic

def main():
    print("📦 Loading delivery data...")
    deliveries = get_upcoming_deliveries()

    print("📊 Loading stock data...")
    stock_data = load_stock_data()

    print("🔍 Matching delivery to stock...")
    shortages = find_stock_shortages(deliveries, stock_data)

    # ✅ Always print full alert message to terminal
    print("\n🧾 Final Stock Shortage Report:")
    print("=" * 60)
    if not shortages:
        print("✅ No stock shortages found.")
    else:
        for item in shortages:
            print(item)
            print("-" * 60)

    # ✅ Still try sending SMS using Twilio
    print("📤 Sending alerts...")
    send_sms_alert(shortages)

if __name__ == "__main__":
    main()
