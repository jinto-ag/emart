import razorpay
from django.conf import settings

RAZORPAY_KEY_ID = settings.RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET = settings.RAZORPAY_KEY_SECRET


def get_client():
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    return client


def create_order(client, amount, callback_url, receipt=None, currency="INR"):
    data = {
        "amount": amount,
        "currency": currency,
        "receipt": receipt,
        "payment_capture": 0,
    }
    order = client.order.create(data=data)
    order_id = order.get("id", None)
    context = {}
    if order_id:
        context = {
            "razorpay_order_id": order_id,
            "razorpay_merchant_key": RAZORPAY_KEY_ID,
            "razorpay_amount": amount,
            "razorpay_currency": currency,
            "razorpay_callback_url": callback_url,
        }
    return context
