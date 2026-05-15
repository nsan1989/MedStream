import requests
from django.conf import settings


# OTP send.
def send_otp(phone, otp):
    url = "https://control.msg91.com/api/v5/flow"

    payload = {
        "template_id": settings.MSG91_SMS_TEMPLATE_ID,
        "short_url": 0,
        "recipients": [
            {
                "mobiles": f"91{phone}",
                "otp": otp,
            }
        ],
    }

    headers = {
        "accept": "application/json",
        "authkey": settings.MSG91_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=5)
    return response.json()
