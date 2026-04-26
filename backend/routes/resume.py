from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request, Query
from fastapi.responses import Response
from fastapi.concurrency import run_in_threadpool
from datetime import datetime
import uuid

from services.mongodb import resumes_collection
from services.ai_service import generate_preview, optimize_resume_full
from services.payment_service import create_razorpay_order, verify_razorpay_signature
from services.pdf_generator import generate_premium_pdf
from utils.file_handler import process_uploaded_file
from core.security import generate_session_token, is_token_expired
from core.logging import logger
from models.resume import PaymentOrderRequest, PaymentVerificationRequest, TrackEventRequest
# Note: In main.py we import Limiter, but let's just assume we don't strictly decorate every route yet, 
# or we can if we import it. For simplicity we'll skip the @limiter.limit decorator here, 
# or we can import from main. To avoid circular imports, we just handle standard FastAPI logic.

router = APIRouter()

@router.post("/upload")
async def upload_resume(
    name: str = Form(...),
    email: str = Form(...),
    plan: str = Form(...),
    file: UploadFile = File(...)
):
    if plan not in ['basic', 'pro', 'premium']:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    content = await file.read()
    
    try:
        resume_text = process_uploaded_file(file.filename, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File processing error: {str(e)}")
    
    if len(resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume too short")
        
    # Cost Control: Cap input at ~15,000 characters to prevent OpenAI token abuse
    if len(resume_text) > 15000:
        resume_text = resume_text[:15000]
    
    resume_id = str(uuid.uuid4())
    
    try:
        preview_data = await run_in_threadpool(generate_preview, resume_text)
    except Exception as e:
        logger.error(f"Failed to generate preview for {resume_id}: {e}")
        raise HTTPException(status_code=500, detail="AI Preview generation failed")

    resumes_collection.insert_one({
        "resume_id": resume_id,
        "name": name,
        "email": email,
        "plan": plan,
        "original_text": resume_text,
        "preview": preview_data,
        "status": "pending_payment",
        "created_at": datetime.utcnow()
    })
    
    return {"resume_id": resume_id, "preview": preview_data, "status": "pending_payment"}

@router.post("/create-order")
async def create_order(req: PaymentOrderRequest):
    resume = resumes_collection.find_one({"resume_id": req.resume_id})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if resume.get("status") in ["processing", "completed"]:
        raise HTTPException(status_code=400, detail="Resume already paid and processed")
    
    prices = {"basic": 199, "pro": 499, "premium": 999}
    amount = prices.get(req.plan, 199)
    
    try:
        order = create_razorpay_order(amount, req.resume_id)
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {e}")
        raise HTTPException(status_code=502, detail="Payment gateway unavailable. Please try again.")
    
    resumes_collection.update_one(
        {"resume_id": req.resume_id},
        {"$set": {"order_id": order["id"], "amount": amount}}
    )
    
    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "plan_name": req.plan
    }

def background_ai_task(resume_id: str, resume_text: str):
    try:
        optimized = optimize_resume_full(resume_text)
        resumes_collection.update_one(
            {"resume_id": resume_id},
            {"$set": {"optimized_data": optimized, "status": "completed"}}
        )
        logger.info(f"Successfully processed resume {resume_id} in background")
    except Exception as e:
        logger.error(f"Background AI failure for {resume_id}: {e}")
        resumes_collection.update_one(
            {"resume_id": resume_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )

@router.post("/verify-payment")
async def verify_payment(req: PaymentVerificationRequest, background_tasks: BackgroundTasks):
    is_valid = verify_razorpay_signature(req.order_id, req.razorpay_payment_id, req.razorpay_signature)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
        
    resume = resumes_collection.find_one({"order_id": req.order_id})
    if not resume:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if resume.get("status") in ["processing", "completed"]:
        return {"status": "already_processed"}

    resumes_collection.update_one(
        {"resume_id": resume["resume_id"]},
        {"$set": {
            "status": "processing", 
            "payment_id": req.razorpay_payment_id,
            "payment_verified_at": datetime.utcnow()
        }}
    )
    
    # Trigger background processing
    background_tasks.add_task(background_ai_task, resume["resume_id"], resume["original_text"])
    
    return {"status": "payment_verified_processing_started"}

@router.get("/status/{resume_id}")
async def get_status(resume_id: str):
    resume = resumes_collection.find_one({"resume_id": resume_id})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"status": resume.get("status", "unknown")}

@router.get("/result/{resume_id}")
async def get_result(resume_id: str):
    resume = resumes_collection.find_one({"resume_id": resume_id})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Resume processing not yet complete")
        
    # Generate secure session token for PDF download
    session_token = generate_session_token()
    resumes_collection.update_one(
        {"resume_id": resume_id},
        {"$set": {"session_token": session_token, "token_created_at": datetime.utcnow()}}
    )
        
    return {
        "optimized_data": resume.get("optimized_data"),
        "session_token": session_token
    }

@router.get("/pdf/{resume_id}")
async def get_pdf(resume_id: str, token: str = Query(...)):
    resume = resumes_collection.find_one({"resume_id": resume_id})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if resume.get("session_token") != token:
        raise HTTPException(status_code=403, detail="Invalid or missing session token")
        
    if is_token_expired(resume.get("token_created_at", datetime.utcnow())):
        raise HTTPException(status_code=403, detail="Session token expired")

    # Prevent event loop blocking under concurrent PDF downloads
    pdf_bytes = await run_in_threadpool(generate_premium_pdf, resume.get("optimized_data", {}))
    
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=optimized_resume_{resume_id[-6:]}.pdf"}
    )

@router.post("/track")
async def track_event(request: Request, event_data: TrackEventRequest):
    # In production, this would pipe to Mixpanel, Amplitude, or BigQuery
    logger.info(f"[ANALYTICS] Event: {event_data.event_name} | Resume: {event_data.resume_id} | Meta: {event_data.event_metadata}")
    return {"status": "logged"}