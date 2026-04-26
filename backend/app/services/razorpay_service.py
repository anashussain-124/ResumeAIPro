import razorpay
from app.config import settings
from app.models.schemas import PlanType

client = razorpay.Client(
    auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
)

PRICING = {
    PlanType.BASIC: {
        "amount": 19900,
        "display": "₹199",
        "name": "Basic Resume Optimization",
        "description": "AI-optimized resume with 1 PDF download"
    },
    PlanType.PRO: {
        "amount": 49900,
        "display": "₹499",
        "name": "Pro Resume + LinkedIn",
        "description": "Resume + LinkedIn optimization with 3 PDF downloads"
    },
    PlanType.PREMIUM: {
        "amount": 99900,
        "display": "₹999",
        "name": "Premium Career Package",
        "description": "Full optimization with 10 downloads + priority support"
    }
}

def create_order(resume_id: str, plan: PlanType) -> dict:
    plan_info = PRICING.get(plan, PRICING[PlanType.BASIC])
    
    order = client.order.create({
        "amount": plan_info["amount"],
        "currency": "INR",
        "receipt": f"resume_{resume_id}",
        "notes": {
            "resume_id": resume_id,
            "plan": plan.value
        }
    })
    
    return {
        "order_id": order["id"],
        "amount": plan_info["amount"],
        "currency": "INR",
        "plan_name": plan_info["name"],
        "key_id": settings.razorpay_key_id
    }

def verify_payment(order_id: str, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
    import hmac
    import hashlib
    
    generated_signature = hmac.new(
        settings.razorpay_key_secret.encode(),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    return generated_signature == razorpay_signature

def get_order_details(order_id: str) -> dict:
    return client.order.fetch(order_id)