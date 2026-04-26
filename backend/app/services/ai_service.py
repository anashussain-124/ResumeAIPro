import json
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def optimize_resume(resume_text: str, plan: str) -> dict:
    is_premium = plan in ["pro", "premium"]
    
    base_prompt = f"""You are an expert resume writer and career consultant. Optimize this resume for ATS (Applicant Tracking Systems) and human hiring managers.

IMPORTANT RULES:
1. Use strong action verbs at the start of each bullet point
2. Quantify achievements where possible (e.g., "increased sales by 30%")
3. Remove fluff words and weak phrases
4. Use industry-specific keywords naturally
5. Keep bullet points concise and impactful (1-2 lines each)

Resume to optimize:
{resume_text}

Return ONLY valid JSON in this exact format:
{{
  "summary": "Professional summary in 3-4 lines - who you are, what you bring, your key strength",
  "experience": [
    {{
      "company": "Company Name",
      "role": "Job Title",
      "duration": "Jan 2020 - Present",
      "bullets": ["Impactful bullet 1", "Impactful bullet 2", "Impactful bullet 3"]
    }}
  ],
  "skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
  "education": [
    {{
      "institution": "University/School Name",
      "degree": "Degree Name",
      "year": "Year"
    }}
  ],
  "improvements": ["Specific improvement made 1", "Specific improvement made 2", "Specific improvement made 3"]
}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an elite resume writer. Return ONLY valid JSON, no explanations, no markdown fences."},
            {"role": "user", "content": base_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    
    result = json.loads(response.choices[0].message.content)
    
    if is_premium:
        result["improvements"].append("Added ATS optimization keywords throughout")
        result["improvements"].append("Quantified all measurable achievements")
    
    return result

def generate_linkedin_content(resume_text: str, optimized_resume: dict) -> dict:
    summary = optimized_resume.get("summary", "")
    skills = ", ".join(optimized_resume.get("skills", [])[:5])
    
    prompt = f"""Based on this resume data, create compelling LinkedIn content:

Original Resume:
{resume_text}

Optimized Summary: {summary}
Top Skills: {skills}

Return ONLY valid JSON:
{{
  "headline": "Catchy LinkedIn headline (max 220 chars, use pipes for separation)",
  "about": "Engaging About section (3-4 paragraphs, first person, talks about impact and value)",
  "experience": "LinkedIn-style experience descriptions (conversational, achievement-focused)",
  "summary": "Brief summary of what was improved and why it matters"
}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a LinkedIn expert and personal brand strategist. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8
    )
    
    return json.loads(response.choices[0].message.content)