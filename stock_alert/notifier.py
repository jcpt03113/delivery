from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms_alert(shortages):
    if not shortages:
        print("✅ No stock issues detected.")
        return

    # Limit message to 8 items max to stay under 1600 characters
    max_items = 8
    message_body = "🚨 Stock Shortage Alert:\n\n"
    message_body += "\n\n".join(shortages[:max_items])

    if len(shortages) > max_items:
        message_body += f"\n\n(+{len(shortages) - max_items} more items...)"

    print("🚧 SMS content preview:\n", message_body)

    print("📤 Sending alerts...")
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_FROM_NUMBER,
        to=TWILIO_TO_NUMBER
    )
    print("✅ Alert sent. SID:", message.sid)
