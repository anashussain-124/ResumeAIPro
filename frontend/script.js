const API_BASE = 'http://localhost:8000/api';

let selectedFile = null;
let currentResumeId = null;
let currentOrderId = null;
let sessionToken = null;
let selectedPlan = 'basic';

const PRICES = {
    basic: 199,
    pro: 499,
    premium: 999
};

async function trackEvent(eventName, metadata = {}) {
    try {
        await fetch(`${API_BASE}/track`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_name: eventName,
                resume_id: currentResumeId,
                event_metadata: metadata
            })
        });
    } catch (e) {
        console.error("Tracking error", e);
    }
}

function selectPlan(plan) {
    selectedPlan = plan;
    document.getElementById('plan').value = plan;
    const uploadSection = document.getElementById('upload-section');
    uploadSection.scrollIntoView({ behavior: 'smooth' });
}

let countdownInterval;
function startCountdown() {
    let time = 15 * 60;
    const timerDisplay = document.getElementById('countdownTimer');
    clearInterval(countdownInterval);
    
    countdownInterval = setInterval(() => {
        let minutes = Math.floor(time / 60);
        let seconds = time % 60;
        timerDisplay.textContent = `Offer Expires in ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        if (time <= 0) {
            clearInterval(countdownInterval);
            timerDisplay.textContent = "Offer Expired. Price may increase.";
        }
        time--;
    }, 1000);
}

async function submitResume() {
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const plan = document.getElementById('plan').value;
    const file = document.getElementById('file').files[0];

    if (!name || !email || !file) {
        alert('Please fill in your name, email, and upload a resume');
        return;
    }

    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');

    trackEvent("upload_started", { plan: plan });

    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    formData.append('plan', plan);
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.detail || 'Upload failed');

        currentResumeId = result.resume_id;
        
        document.getElementById('atsScore').textContent = result.preview.ats_score;
        document.getElementById('previewBefore').textContent = result.preview.before_example;
        document.getElementById('previewAfter').textContent = result.preview.after_example;
        document.getElementById('previewHook').textContent = result.preview.hook_message;
        document.getElementById('improvementsFound').textContent = result.preview.improvements_found;
        document.getElementById('previewPaymentAmount').textContent = `₹${PRICES[plan]}`;
        
        document.getElementById('upload-section').classList.add('hidden');
        document.getElementById('previewSection').classList.remove('hidden');
        document.getElementById('previewSection').scrollIntoView({ behavior: 'smooth' });

        trackEvent("preview_seen", { ats_score: result.preview.ats_score });
        startCountdown();

    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
    }
}

async function initiatePayment() {
    const plan = document.getElementById('plan').value;
    trackEvent("payment_initiated", { plan: plan });
    try {
        const orderResponse = await fetch(`${API_BASE}/create-order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_id: currentResumeId, plan: plan })
        });

        const orderData = await orderResponse.json();
        if (!orderResponse.ok) throw new Error(orderData.detail || 'Failed to create order');

        currentOrderId = orderData.order_id;

        const options = {
            key: orderData.key_id || 'rzp_test_dummy', 
            amount: orderData.amount,
            currency: 'INR',
            name: 'Interview Magnet',
            description: orderData.plan_name,
            order_id: orderData.order_id,
            prefill: {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value
            },
            theme: { color: '#e94560' },
            handler: async function(response) {
                await verifyPayment(response);
            }
        };

        const razorpay = new Razorpay(options);
        razorpay.open();
    } catch (error) {
        alert(`Payment Error: ${error.message}`);
    }
}

async function verifyPayment(response) {
    try {
        const verifyResponse = await fetch(`${API_BASE}/verify-payment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                order_id: currentOrderId,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature
            })
        });

        if (!verifyResponse.ok) throw new Error('Payment verification failed');

        trackEvent("payment_success", { order_id: currentOrderId });

        document.getElementById('previewSection').classList.add('hidden');
        document.getElementById('pollingSection').classList.remove('hidden');
        document.getElementById('pollingSection').scrollIntoView({ behavior: 'smooth' });
        
        pollStatus();

    } catch (error) {
        alert(`Verification Error: ${error.message}`);
    }
}

async function pollStatus() {
    let attempts = 0;
    const maxAttempts = 40; // 120 seconds max
    
    const interval = setInterval(async () => {
        attempts++;
        if (attempts > maxAttempts) {
            clearInterval(interval);
            alert('AI optimization is taking longer than expected. Please check your email or contact support.');
            return;
        }
        try {
            const res = await fetch(`${API_BASE}/status/${currentResumeId}`);
            const data = await res.json();
            
            if (data.status === 'completed') {
                clearInterval(interval);
                showFinalResults();
            } else if (data.status === 'failed') {
                clearInterval(interval);
                alert('AI optimization failed. Please contact support.');
            }
        } catch (e) {
            console.error("Polling error", e);
        }
    }, 3000);
}

async function showFinalResults() {
    try {
        const response = await fetch(`${API_BASE}/result/${currentResumeId}`);
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || 'Failed to fetch results');

        sessionToken = data.session_token;
        
        document.getElementById('pollingSection').classList.add('hidden');
        document.getElementById('resultsSection').classList.remove('hidden');
        
        document.getElementById('paymentSection').classList.add('hidden');
        document.getElementById('downloadSection').classList.remove('hidden');
        document.getElementById('resumeIdDisplay').textContent = `Resume ID: ${currentResumeId}`;

        displayResults(data.optimized_data);
        trackEvent("result_viewed");

    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

function displayResults(opt) {
    document.getElementById('contentResults').classList.remove('hidden');
    document.getElementById('contentResults').scrollIntoView({ behavior: 'smooth' });

    const display = document.getElementById('contentDisplay');
    let html = '';

    if (opt.summary) {
        html += `<div class="content-section"><h3>📝 Professional Summary</h3><p>${opt.summary}</p></div>`;
    }

    if (opt.experience && opt.experience.length > 0) {
        html += `<div class="content-section"><h3>💼 Work Experience</h3>`;
        opt.experience.forEach(exp => {
            html += `
                <div style="margin-bottom: 20px;">
                    <strong>${exp.role}</strong> at ${exp.company} (${exp.duration})<br>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        ${(exp.bullets || []).map(b => `<li>${b}</li>`).join('')}
                    </ul>
                </div>
            `;
        });
        html += `</div>`;
    }

    if (opt.skills && opt.skills.length > 0) {
        html += `<div class="content-section"><h3>🎯 Core Skills</h3><p>${opt.skills.join(' • ')}</p></div>`;
    }

    if (opt.education && opt.education.length > 0) {
        html += `<div class="content-section"><h3>🎓 Education</h3>`;
        opt.education.forEach(edu => {
            html += `<p><strong>${edu.degree}</strong>, ${edu.institution} (${edu.year})</p>`;
        });
        html += `</div>`;
    }

    display.innerHTML = html;
}

function viewResults() {
    document.getElementById('contentResults').scrollIntoView({ behavior: 'smooth' });
}

function downloadPDF() {
    if (!sessionToken) {
        alert('Invalid session. Please reload.');
        return;
    }
    trackEvent("pdf_downloaded");
    window.location.href = `${API_BASE}/pdf/${currentResumeId}?token=${sessionToken}`;
}

const fileUpload = document.getElementById('fileUpload');
const fileInput = document.getElementById('file');
const fileNameDisplay = document.getElementById('fileName');

fileUpload.addEventListener('click', () => fileInput.click());
fileUpload.addEventListener('dragover', (e) => { e.preventDefault(); fileUpload.classList.add('dragover'); });
fileUpload.addEventListener('dragleave', () => { fileUpload.classList.remove('dragover'); });
fileUpload.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUpload.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleFile(e.target.files[0]);
});

function handleFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['pdf', 'docx', 'doc', 'txt'].includes(ext)) {
        alert('Please upload a PDF, DOCX, or TXT file');
        return;
    }
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        return;
    }
    fileNameDisplay.innerHTML = `✅ Selected: ${file.name}`;
    fileNameDisplay.style.display = 'block';
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
});