from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json
from jobs.models import Job
import google.generativeai as genai
from pgvector.django import CosineDistance


# -------------------------------
# 🔹 GEMINI SETUP
# -------------------------------

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={"temperature": 0.2}
)

# -------------------------------
# 🔹 EMBEDDING MODEL (FIXED)
# -------------------------------

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# -------------------------------
# 🔹 QUERY PARSER (GEMINI)
# -------------------------------

def parse_query(query):

    prompt = f"""
    Extract:
    - skill
    - location

    Query: {query}

    Return ONLY valid JSON:
    {{
        "skill": "...",
        "location": "..."
    }}
    """

    try:
        res = model.generate_content(prompt)
        content = res.text.strip()

        # 🔥 CLEAN RESPONSE
        content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)

    except Exception as e:
        print("Parse Error:", e)
        return {"skill": "", "location": ""}

# -------------------------------
# 🔹 EMBEDDING GENERATION
# -------------------------------

def generate_embedding(text):
    return embedding_model.encode(text).tolist()

# -------------------------------
# 🔹 BUILD JOB TEXT
# -------------------------------

def build_job_text(job):
    return f"""
    Title: {job.get('title')}
    Company: {job.get('company')}
    Skills: {', '.join(job.get('skills', []))}
    Description: {job.get('description')}
    """

# -------------------------------
# 🔹 COSINE SIMILARITY
# -------------------------------

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0

    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# -------------------------------
# 🔹 SEMANTIC SEARCH (CURRENT)
# -------------------------------

def semantic_search(query, top_k=5):

    query_embedding = generate_embedding(query)

    jobs = Job.objects.exclude(embedding=None)

    scored_jobs = []

    for job in jobs:

        if not job.embedding:
            continue

        score = cosine_similarity(query_embedding, job.embedding)

        scored_jobs.append((score, job))

    # Sort highest similarity first
    scored_jobs.sort(reverse=True, key=lambda x: x[0])

    results = []

    for score, job in scored_jobs[:top_k]:
        results.append({
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "score": round(score, 3)
        })

    return results

# -------------------------------
# 🔹 INTERVIEW QUESTIONS (GEMINI)
# -------------------------------

def generate_questions(skill):

    prompt = f"""
    Generate 5 interview questions for {skill}.
    Keep them concise and practical.
    """

    try:
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        print("Question Error:", e)
        return "No questions generated"

# -------------------------------
# 🔹 EXPLAINABILITY (GEMINI FIXED)
# -------------------------------

def explain_job_match(query, job):

    prompt = f"""
    Explain why this job matches:

    Query: {query}
    Job: {job.title} at {job.company}
    Skills: {job.skills}
    """

    try:
        res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        print("Explain Error:", e)
        return "No explanation available"