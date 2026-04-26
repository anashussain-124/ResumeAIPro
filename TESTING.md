# Testing Guide - ResumeAI Pro

## LOCAL SETUP

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env`:
```env
MONGODB_URI=mongodb://localhost:27017/resume_builder
OPENAI_API_KEY=sk-your-key-here
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### 3. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Backend should be running at: http://localhost:8000

---

## API TESTING

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "service": "resume-builder-api"}
```

### Upload Resume

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "name=Test User" \
  -F "email=test@example.com" \
  -F "plan=basic" \
  -F "file=@test_resume.pdf"
```

Expected response:
```json
{
  "success": true,
  "resume_id": "uuid-string",
  "status": "completed",
  "message": "Resume optimized successfully. Please complete payment to download."
}
```

### Check Status

```bash
curl "http://localhost:8000/api/status/{resume_id}"
```

### Get Plans

```bash
curl "http://localhost:8000/api/plans"
```

---

## BROWSER TESTING

### Test the Frontend

1. Open `frontend/index.html` in browser
2. Fill in name and email
3. Select a plan
4. Upload a test resume file
5. Click "Optimize My Resume"
6. Verify loading state appears
7. Verify results section shows
8. Test payment flow

---

## PAYMENT TESTING (Razorpay)

### Test Mode

1. Use Razorpay Dashboard Test Mode
2. Use test card: 4111 1111 1111 1111
3. Any future expiry date
4. Any CVV

### Test Flow

```bash
# 1. Create order
curl -X POST "http://localhost:8000/api/create-order" \
  -H "Content-Type: application/json" \
  -d '{"resume_id": "test-id", "plan": "basic"}'

# 2. Get order_id from response
# 3. Complete payment in browser with test card
# 4. Verify payment
curl -X POST "http://localhost:8000/api/verify-payment" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order_xxx",
    "razorpay_order_id": "order_xxx",
    "razorpay_payment_id": "pay_xxx",
    "razorpay_signature": "signature"
  }'
```

---

## ERROR TESTING

| Scenario | Test | Expected |
|----------|------|----------|
| Invalid file type | Upload .exe | Error: File type not supported |
| Large file | Upload 15MB file | Error: File too large |
| Missing fields | Submit without name | Error: validation error |
| No file | Submit empty form | Error: Please upload resume |
| Short resume | Upload 1-line file | Error: Resume too short |
| Wrong order | Verify fake payment | Error: Payment verification failed |
| No payment | Access /result/{id} without payment | Error: Payment required |

---

## PERFORMANCE TESTING

```bash
# Test concurrent uploads
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/upload" \
    -F "name=User$i" \
    -F "email=user$i@test.com" \
    -F "plan=basic" \
    -F "file=@test_resume.pdf" &
done
```

Monitor response times and database connections.

---

## MANUAL TEST CHECKLIST

### Frontend
- [ ] Landing page loads correctly
- [ ] All pricing cards display
- [ ] File upload works (drag & drop)
- [ ] File validation shows errors
- [ ] Form submission shows loader
- [ ] Results section displays
- [ ] Payment initiates correctly
- [ ] Download works after payment

### Backend
- [ ] Health endpoint returns 200
- [ ] Upload creates database entry
- [ ] Status shows correct state
- [ ] Order creation works
- [ ] Payment verification works
- [ ] PDF generation completes
- [ ] PDF download works
- [ ] Results endpoint returns data

### Integration
- [ ] Upload → AI → Save flow works
- [ ] Payment → Verification → Unlock works
- [ ] Download after payment works
- [ ] All error states handled