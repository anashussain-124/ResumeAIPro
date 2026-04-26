# Deployment Guide - ResumeAI Pro

## PREREQUISITES

- GitHub account
- MongoDB Atlas account (free tier)
- OpenAI API key
- Razorpay account (for India) or Stripe (for international)
- Vercel account (frontend)
- Railway/Render account (backend)

---

## STEP 1: SETUP MONGODB ATLAS

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up / Login
3. Create a free cluster:
   - Choose AWS/Mumbai (for India) or nearest region
   - Select M0 Sandbox (free tier)
   - Create cluster (takes 3-5 minutes)
4. Create database user:
   - Security → + ADD NEW USER
   - Username: resume_admin
   - Password: [strong-password]
   - Role: Read and write to any database
5. Whitelist IP:
   - Security → IP Access List
   - ADD IP ADDRESS: 0.0.0.0/0 (allow all for now)
6. Get connection string:
   - Clusters → CONNECT → Connect your application
   - Copy connection string
   - Format: `mongodb+srv://resume_admin:PASSWORD@cluster.mongodb.net/resume_builder`

---

## STEP 2: SETUP OPENAI API

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up / Login
3. API Keys → Create new secret key
4. Copy the key (starts with `sk-`)
5. Add payment method (required for API usage)
6. Typical cost: ~$0.50-2 per resume optimization

---

## STEP 3: SETUP RAZORPAY (India)

1. Go to [dashboard.razorpay.com](https://dashboard.razorpay.com)
2. Sign up / Login
3. Settings → API Keys
4. Generate Key ID and Key Secret
5. Keep these ready for backend config

---

## STEP 4: DEPLOY BACKEND TO RAILWAY

### Option A: Railway (Recommended)

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. New Project → Deploy from GitHub repo
4. Select your repository
5. Add Environment Variables:
   ```
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/resume_builder
   OPENAI_API_KEY=sk-xxxxx
   RAZORPAY_KEY_ID=rzp_xxxxx
   RAZORPAY_KEY_SECRET=xxxxx
   FRONTEND_URL=https://your-app.vercel.app
   ```
6. Railway will auto-detect Python and install requirements
7. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
8. Deploy!

### Option B: Render

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. New → Web Service
4. Connect GitHub repo
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables (same as Railway)
7. Deploy

### Option C: VPS (DigitalOcean/Ubuntu)

```bash
# SSH into server
ssh root@your-server-ip

# Install Python and dependencies
apt update && apt install -y python3 python3-pip nginx

# Clone repository
git clone https://github.com/your-username/resume-builder.git
cd resume-builder/backend

# Install dependencies
pip3 install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/resume-builder.service << EOF
[Unit]
Description=Resume Builder API
After=network.target

[Service]
User=www-data
WorkingDirectory=/root/resume-builder/backend
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl enable resume-builder
systemctl start resume-builder

# Configure Nginx
cat > /etc/nginx/sites-available/resume-builder << EOF
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/resume-builder /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

## STEP 5: DEPLOY FRONTEND TO VERCEL

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. New Project → Import from GitHub
4. Select the repository
5. Framework: Other
6. Build Command: (leave empty)
7. Environment Variables:
   ```
   API_URL=https://api.your-backend.railway.app/api
   ```
8. Deploy!

---

## STEP 6: UPDATE FRONTEND API URL

In `frontend/script.js`, update the API base URL:

```javascript
// For production, use your deployed backend URL
const API_BASE = 'https://api.your-backend.railway.app/api';
```

---

## STEP 7: CONFIGURE RAZORPAY WHITELIST (Production)

For Razorpay, add your production domain:
- Dashboard → Settings → API Keys
- Update allowed domains in your frontend Razorpay configuration

---

## ENVIRONMENT VARIABLES CHECKLIST

### Backend (.env for local, Railway/Render for production)
```
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/resume_builder
OPENAI_API_KEY=sk-xxxxx
RAZORPAY_KEY_ID=rzp_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend (Vercel)
```
API_URL=https://api.your-backend.railway.app
```

---

## CUSTOM DOMAIN SETUP

### Backend (Railway)
- Railway Dashboard → Project → Settings → Domains
- Add custom domain (api.resumeaipro.com)
- Add DNS record in your registrar

### Frontend (Vercel)
- Vercel Dashboard → Project → Domains
- Add custom domain (www.resumeaipro.com)
- Configure DNS

### Recommended DNS Records
```
A record: @ → your-vercel-ip
CNAME: www → your-vercel-domain.vercel.app
CNAME: api → your-railway-domain.railway.app
```

---

## SSL CERTIFICATE

Both Railway and Vercel provide free SSL automatically.

For VPS, use Let's Encrypt:
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## MONITORING

### Backend Logs
- Railway: Dashboard → Deployments → Logs
- Render: Dashboard → Logs
- VPS: `journalctl -u resume-builder -f`

### Health Check
```bash
curl https://api.your-backend.com/health
# Should return: {"status": "healthy", "service": "resume-builder-api"}
```

### MongoDB Monitoring
- Atlas Dashboard → Metrics
- Track queries, connections, storage

---

## COST ESTIMATION (Monthly)

| Service | Plan | Cost |
|---------|------|------|
| MongoDB Atlas | M0 Free | $0 |
| OpenAI API | Pay-as-you-go | $5-50 |
| Railway | Starter | $0-5 |
| Vercel | Hobby | $0 |
| Domain | .com | $10-15 |
| **Total** | | **$15-70/mo** |

---

## BACKUP STRATEGY

### MongoDB Atlas
- Automatic daily backups (M0 tier)
- Point-in-time recovery available

### Local Files
- Generated PDFs stored on server
- Consider S3 backup for production

---

## SECURITY CHECKLIST

- [ ] MongoDB password is strong
- [ ] IP whitelist configured (production)
- [ ] API keys not in GitHub
- [ ] HTTPS enforced
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] File upload size limits enforced
- [ ] Payment signature verification working