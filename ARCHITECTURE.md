# Resume Builder SaaS - Complete System

## 1. SYSTEM ARCHITECTURE

```
INPUT                    PROCESS                    OUTPUT                    STORAGE                    DELIVERY
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
User uploads        →   File Validator       →   Text Extraction     →   MongoDB            →   Download Link
PDF/DOCX/TXT            (check size/type)         (PyPDF/DOCX)              (Atlas)           →   Email (future)
                        ↓
                   AI Optimizer
                   (GPT-4o)
                        ↓
                   PDF Generator
                   (ReportLab)
                        ↓
                   Payment Gate
                   (Razorpay) ───────────────────────────→ UNLOCK RESULT
```

## 2. USER FLOW

```
User ──→ Landing Page ──→ Upload Resume ──→ Pay (₹199-999) ──→ Processing ──→ Download PDF
                  │            │                    │               │
                  │            │                    │               │
              [Landing]    [File stored]        [Payment ID]    [AI optimizes]
                                                                  [PDF generated]
```

## 3. PRICING TIERS

| Plan | Price | Features |
|------|-------|----------|
| Basic | ₹199 | Resume optimization + 1 PDF download |
| Pro | ₹499 | Resume + LinkedIn optimization + 3 downloads |
| Premium | ₹999 | Full suite + 10 downloads + priority processing |

## 4. API DESIGN

```
POST   /api/upload              → Upload resume, get resume_id
GET    /api/status/{id}         → Check processing status
POST   /api/create-order        → Create Razorpay order
POST   /api/verify-payment      → Verify payment, unlock result
GET    /api/result/{id}         → Get optimized result (after payment)
GET    /api/pdf/{id}            → Download PDF (after payment)
POST   /api/generate-linkedin   → Generate LinkedIn content
```

## 5. DATABASE SCHEMA (MongoDB)

```javascript
// resumes collection
{
  _id: ObjectId,
  resume_id: String (UUID),
  name: String,
  email: String,
  plan: String ("basic"/"pro"/"premium"),
  original_filename: String,
  original_text: String,
  optimized_data: {
    summary: String,
    experience: [{ company, role, duration, bullets: [] }],
    skills: [String],
    education: [{ institution, degree, year }]
  },
  linkedin_content: {
    headline: String,
    about: String,
    experience: String
  },
  pdf_path: String,
  status: String ("pending"/"processing"/"completed"/"failed"),
  payment_id: String,
  payment_verified: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}

// orders collection
{
  _id: ObjectId,
  order_id: String (Razorpay order_id),
  resume_id: String,
  amount: Int,
  currency: String,
  status: String ("created"/"paid"/"failed"),
  created_at: DateTime
}
```