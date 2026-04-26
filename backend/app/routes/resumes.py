from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from datetime import datetime
from app.database import resumes_collection, orders_collection
from app.services.ai_service import optimize_resume, generate_linkedin_content
from app.services.pdf_generator import generate_resume_pdf
from app.services.razorpay_service import create_order, verify_payment, PRICING
from app.utils.file_handler import FileHandler
from app.models.schemas import (
    PlanType, StatusType, ResumeUploadRequest,
    OrderCreateRequest, PaymentVerifyRequest
)
import uuid
import os
import json

router = APIRouter()

UPLOAD_DIR = "uploads"
PDF_DIR = "generated_pdfs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(
    name: str = Form(...),
    email: str = Form(...),
    plan: str = Form(...),
    file: UploadFile = File(...)
):
    if plan not in [p.value for p in PlanType]:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    is_valid, message = FileHandler.validate_file(file.filename, file.size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    content = await file.read()
    
    try:
        resume_text = FileHandler.extract_text(file.filename, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read file: {str(e)}")
    
    if len(resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume content too short")
    
    resume_id = str(uuid.uuid4())
    
    resumes_collection.insert_one({
        "resume_id": resume_id,
        "name": name,
        "email": email,
        "plan": plan,
        "original_filename": file.filename,
        "original_text": resume_text,
        "status": "processing",
        "payment_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    try:
        optimized = optimize_resume(resume_text, plan)
        
        linkedin_data = None
        if plan in [p.value for p in [PlanType.PRO, PlanType.PREMIUM]]:
            linkedin_data = generate_linkedin_content(resume_text, optimized)
        
        pdf_filename = f"{resume_id}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        generate_resume_pdf(name, email, optimized, pdf_path)
        
        resumes_collection.update_one(
            {"resume_id": resume_id},
            {"$set": {
                "optimized_data": optimized,
                "linkedin_content": linkedin_data,
                "pdf_path": pdf_path,
                "status": "completed",
                "updated_at": datetime.utcnow()
            }}
        )
    except Exception as e:
        resumes_collection.update_one(
            {"resume_id": resume_id},
            {"$set": {"status": "failed", "error": str(e)}}
        })
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    return {
        "success": True,
        "resume_id": resume_id,
        "status": "completed",
        "message": "Resume optimized successfully. Please complete payment to download."
    }

@router.get("/status/{resume_id}")
async def get_status(resume_id: str):
    resume = resumes_collection.find_one({"resume_id": resume_id}, {"_id": 0, "status": 1, "plan": 1})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@router.post("/create-order")
async def create_payment_order(request: OrderCreateRequest):
    resume = resumes_collection.find_one({"resume_id": request.resume_id})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    plan = PlanType(request.plan)
    order_data = create_order(request.resume_id, plan)
    
    orders_collection.insert_one({
        "order_id": order_data["order_id"],
        "razorpay_order_id": order_data["order_id"],
        "resume_id": request.resume_id,
        "amount": order_data["amount"],
        "currency": order_data["currency"],
        "status": "created",
        "created_at": datetime.utcnow()
    })
    
    return order_data

@router.post("/verify-payment")
async def verify_payment_and_unlock(request: PaymentVerifyRequest):
    is_valid = verify_payment(
        request.order_id,
        request.razorpay_order_id,
        request.razorpay_payment_id,
        request.razorpay_signature
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    order = orders_collection.find_one({"razorpay_order_id": request.razorpay_order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    resumes_collection.update_one(
        {"resume_id": order["resume_id"]},
        {"$set": {
            "payment_id": request.razorpay_payment_id,
            "payment_verified": True,
            "updated_at": datetime.utcnow()
        }}
    )
    
    orders_collection.update_one(
        {"razorpay_order_id": request.razorpay_order_id},
        {"$set": {"status": "paid"}}
    )
    
    return {"success": True, "message": "Payment verified successfully"}

@router.get("/result/{resume_id}")
async def get_result(resume_id: str):
    resume = resumes_collection.find_one(
        {"resume_id": resume_id},
        {"_id": 0, "optimized_data": 1, "linkedin_content": 1, "payment_verified": 1}
    )
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not resume.get("payment_verified"):
        raise HTTPException(status_code=403, detail="Payment required to view results")
    
    return {
        "success": True,
        "resume_id": resume_id,
        "optimized_data": resume.get("optimized_data"),
        "linkedin_content": resume.get("linkedin_content")
    }

@router.get("/pdf/{resume_id}")
async def download_pdf(resume_id: str):
    resume = resumes_collection.find_one(
        {"resume_id": resume_id},
        {"_id": 0, "pdf_path": 1, "name": 1, "payment_verified": 1}
    )
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if not resume.get("payment_verified"):
        raise HTTPException(status_code=403, detail="Payment required to download PDF")
    
    pdf_path = resume.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"optimized_resume_{resume['name'].replace(' ', '_')}.pdf"
    )

@router.get("/plans")
async def get_plans():
    return {
        "plans": [
            {"id": "basic", "name": "Basic", "price": 199, "features": ["Resume optimization", "1 PDF download"]},
            {"id": "pro", "name": "Pro", "price": 499, "features": ["Resume + LinkedIn", "3 PDF downloads"]},
            {"id": "premium", "name": "Premium", "price": 999, "features": ["Full optimization", "10 downloads", "Priority support"]}
        ]
    }