from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class ExperienceEntry(BaseModel):
    company: str
    role: str
    duration: str
    bullets: List[str]

class EducationEntry(BaseModel):
    institution: str
    degree: str
    year: str

class OptimizedResume(BaseModel):
    summary: str
    experience: List[ExperienceEntry]
    skills: List[str]
    education: List[EducationEntry]
    improvements: List[str]

class PreviewData(BaseModel):
    extracted_text_preview: str
    improvements_found: int
    hook_message: str

class ResumeRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    plan: str = Field(..., pattern="^(basic|pro|premium)$")

class PaymentOrderRequest(BaseModel):
    resume_id: str
    plan: str = Field(..., pattern="^(basic|pro|premium)$")

class PaymentVerificationRequest(BaseModel):
    order_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class TrackEventRequest(BaseModel):
    event_name: str
    resume_id: Optional[str] = None
    event_metadata: Optional[dict] = {}