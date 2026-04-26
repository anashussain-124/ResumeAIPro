import razorpay
import hmac
import hashlib
from core.config import settings
from core.logging import logger

def get_razorpay_client():
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        logger.warning("Razorpay keys not set. Payment will fail in production.")
        # Return mock object or handle gracefully if keys missing
        return razorpay.Client(auth=("dummy_key", "dummy_secret"))
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

client = get_razorpay_client()

def create_razorpay_order(amount_inr: int, receipt_id: str) -> dict:
    try:
        order_data = {
            "amount": amount_inr * 100,
            "currency": "INR",
            "receipt": receipt_id,
            "payment_capture": 1
        }
        order = client.order.create(data=order_data)
        return order
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {e}")
        raise ValueError("Payment gateway error")

def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    try:
        msg = f"{order_id}|{payment_id}"
        generated_signature = hmac.new(
            settings.razorpay_key_secret.encode('utf-8'),
            msg.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(generated_signature, signature)
    except Exception as e:
        logger.error(f"Signature verification failed: {e}")
        return False
