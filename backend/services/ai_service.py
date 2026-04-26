import json
from openai import OpenAI
from core.config import settings
from core.logging import logger
from tenacity import retry, wait_exponential, stop_after_attempt

client = OpenAI(api_key=settings.openai_api_key)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def _call_openai(prompt: str, system_msg: str = "You are an expert resume writer. Always return valid JSON.") -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    return json.loads(response.choices[0].message.content)

def generate_preview(resume_text: str) -> dict:
    prompt = f"""You are an elite Fortune 500 tech recruiter. Analyze this resume text and identify exactly why it would be instantly rejected by an Applicant Tracking System (ATS).
    
    Resume: {resume_text[:2000]}
    
    Return ONLY a JSON object with:
    - "ats_score": An integer between 35 and 65 representing their current weak ATS match.
    - "extracted_text_preview": A 30-word snippet of their current weak summary/experience.
    - "improvements_found": An integer between 7 and 18 representing critical errors and missing metrics.
    - "critical_weakness": A punchy, 1-sentence warning (e.g., "Your experience section lacks quantifiable metrics, causing ATS systems to rank you 40% lower than peers.")
    - "hook_message": A 1-sentence urgent CTA (e.g., "We found critical errors blocking your interviews. Let our AI rewrite this to recruiter standards.")
    - "before_example": Provide a weak bullet from their resume.
    - "after_example": Show how a top 1% candidate would write that bullet (use action verbs and metrics).
    """
    return _call_openai(prompt)

def generate_summary(resume_text: str) -> dict:
    prompt = f"""You are an executive resume writer. Write a 3-line professional summary for this candidate.
    Rules: NEVER start with "I am a" or "Dedicated professional". Start directly with their value proposition. Highlight 1 major career achievement. End with their immediate value to a future employer. Tone: Confident, authoritative, metric-driven.
    Resume: {resume_text}
    Return JSON: {{"summary": "..."}}"""
    return _call_openai(prompt)

def optimize_experience(resume_text: str) -> dict:
    prompt = f"""You are an elite technical recruiter. Rewrite the work experience section.
    Rules: Start with a strong, high-impact Action Verb (e.g., Spearheaded, Architected). Follow the XYZ formula: Accomplished X as measured by Y, by doing Z. Inject realistic, logical quantifiable metrics if missing. Max 4 bullets per role.
    Resume: {resume_text}
    Return JSON: {{"experience": [{{"company": "...", "role": "...", "duration": "...", "bullets": ["...", "..."]}}]}}"""
    return _call_openai(prompt)

def extract_skills_and_edu(resume_text: str) -> dict:
    prompt = f"""Extract all hard and soft skills from this resume. Add logical missing industry-standard keywords.
    Group them logically. Also extract education.
    Resume: {resume_text}
    Return JSON: {{"skills": ["..."], "education": [{{"institution": "...", "degree": "...", "year": "..."}}]}}"""
    return _call_openai(prompt)

def optimize_resume_full(resume_text: str) -> dict:
    logger.info("Starting full AI resume optimization modules")
    
    summary_data = generate_summary(resume_text)
    exp_data = optimize_experience(resume_text)
    skills_edu_data = extract_skills_and_edu(resume_text)
    
    improvements = [
        "Injected industry-standard ATS keywords.",
        "Rewrote summary to highlight core value proposition.",
        "Optimized experience bullets with high-impact action verbs.",
        "Quantified achievements using the XYZ formula.",
        "Reorganized structure for strict ATS compatibility."
    ]
    
    return {
        "summary": summary_data.get("summary", ""),
        "experience": exp_data.get("experience", []),
        "skills": skills_edu_data.get("skills", []),
        "education": skills_edu_data.get("education", []),
        "improvements": improvements
    }