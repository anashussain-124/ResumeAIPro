from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class PlanType(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    PREMIUM = "premium"

class StatusType(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExperienceEntry(BaseModel):
    company: str
    role: str
    duration: str
    bullets: List[str]

class EducationEntry(BaseModel):
    institution: str
    degree: str
    year: str

class OptimizedData(BaseModel):
    summary: str
    experience: List[ExperienceEntry]
    skills: List[str]
    education: List[EducationEntry]
    improvements: List[str]

class LinkedInContent(BaseModel):
    headline: str
    about: str
    experience: str
    summary: str

class ResumeUploadRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    plan: PlanType = PlanType.BASIC

class ResumeDocument(BaseModel):
    resume_id: str
    name: str
    email: str
    plan: str
    original_filename: str
    original_text: str
    optimized_data: Optional[OptimizedData] = None
    linkedin_content: Optional[LinkedInContent] = None
    pdf_path: Optional[str] = None
    status: str = StatusType.PENDING
    payment_id: Optional[str] = None
    payment_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreateRequest(BaseModel):
    resume_id: str
    plan: PlanType

class PaymentVerifyRequest(BaseModel):
    order_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class OrderDocument(BaseModel):
    order_id: str
    razorpay_order_id: str
    resume_id: str
    amount: int
    currency: str = "INR"
    status: str = "created"
    created_at: datetime = Field(default_factory=datetime.utcnow)