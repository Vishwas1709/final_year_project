from twilio.rest import Client

# Twilio credentials (keep these safe and use environment variables in production)
account_sid = 'ACda0f9a91bf604f5401c49a012eff3e47'
auth_token = '6fcb65dee069563cbfa4971743484f2a'
twilio_number = '+15415378484'  # Your Twilio phone number

client = Client(account_sid, auth_token)

def send_sms(to_number, message):
    try:
        message = client.messages.create(
            body=message,
            from_=twilio_number,
            to=to_number
        )
        print(f"SMS sent to {to_number}, SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False
