import os
import sys
import json
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

# Add the project root to sys.path so we can import research modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research.models import KeywordMatching, GraphMatching

app = FastAPI(title="Graph Job Recommendation Research API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────

def _load_dataset():
    """Load the real dataset with ground truth."""
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "research", "dataset_real_with_ground_truth.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _clean_title(title):
    """Clean raw job title for display."""
    display = title.replace("Live_", "").replace("_", " ")
    parts = display.rsplit(" ", 1)
    if parts[-1].isdigit():
        display = parts[0]
    return display


def precision_at_k(recommended_jobs, relevant_jobs, k=5):
    if not recommended_jobs:
        return 0.0
    top_k = recommended_jobs[:k]
    relevant_set = set(relevant_jobs)
    hits = sum(1 for job in top_k if job in relevant_set)
    return hits / k


# ──────────────────────────────────────────────
# GET /api/metrics — Evaluation metrics for charts
# ──────────────────────────────────────────────

@app.get("/api/metrics")
async def get_metrics():
    dataset = _load_dataset()
    resumes = dataset["resumes"]
    jobs = dataset["jobs"]
    ground_truth = dataset["ground_truth"]

    keyword_model = KeywordMatching()
    graph_model = GraphMatching()

    k_val = 5
    kw_precisions = []
    gr_precisions = []
    kw_recalls = []
    gr_recalls = []
    kw_all_recs = set()
    gr_all_recs = set()
    graph_only_jobs = set()

    for candidate in resumes:
        c_id = candidate["id"]
        c_skills = candidate["skills"]
        relevant = ground_truth.get(c_id, [])
        relevant_set = set(relevant)

        kw_scores = []
        gr_scores = []

        for job in jobs:
            kw_s = keyword_model.get_score(c_skills, job["required_skills"])
            gr_s = graph_model.get_score(c_skills, job["required_skills"])
            kw_scores.append((job["id"], kw_s))
            gr_scores.append((job["id"], gr_s))

        kw_ranked = [j[0] for j in sorted(kw_scores, key=lambda x: x[1], reverse=True)]
        gr_ranked = [j[0] for j in sorted(gr_scores, key=lambda x: x[1], reverse=True)]

        kw_top = kw_ranked[:k_val]
        gr_top = gr_ranked[:k_val]

        # Precision
        kw_precisions.append(precision_at_k(kw_ranked, relevant, k=k_val))
        gr_precisions.append(precision_at_k(gr_ranked, relevant, k=k_val))

        # Recall
        if relevant:
            kw_recalls.append(len(set(kw_top) & relevant_set) / len(relevant_set))
            gr_recalls.append(len(set(gr_top) & relevant_set) / len(relevant_set))

        # Diversity tracking
        kw_all_recs.update(kw_top)
        gr_all_recs.update(gr_top)

        # Novelty — jobs graph found that keyword missed
        graph_only_jobs.update(set(gr_top) - set(kw_top))

    avg = lambda lst: sum(lst) / len(lst) if lst else 0

    graph_model.close()

    return {
        "k": k_val,
        "candidates": len(resumes),
        "total_jobs": len(jobs),
        "precision": {
            "keyword": round(avg(kw_precisions) * 100, 1),
            "graph": round(avg(gr_precisions) * 100, 1),
        },
        "recall": {
            "keyword": round(avg(kw_recalls) * 100, 1),
            "graph": round(avg(gr_recalls) * 100, 1),
        },
        "diversity": {
            "keyword": len(kw_all_recs),
            "graph": len(gr_all_recs),
        },
        "novelty": {
            "graph_only_count": len(graph_only_jobs),
            "description": f"Graph discovered {len(graph_only_jobs)} unique jobs that keyword matching missed entirely"
        }
    }


# ──────────────────────────────────────────────
# GET /api/graph — Neo4j skill graph data
# ──────────────────────────────────────────────

@app.get("/api/graph")
async def get_graph():
    graph_model = GraphMatching()
    query = """
    MATCH (n:Skill)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    nodes = set()
    edges = []

    with graph_model.driver.session() as session:
        result = session.run(query)
        for record in result:
            n = record["n"]
            if n:
                nodes.add((n["name"], "Skill"))
            m = record["m"]
            if m:
                nodes.add((m["name"], "Skill"))
                edges.append({
                    "source": n["name"],
                    "target": m["name"],
                    "type": record["r"].type
                })

    graph_model.close()

    return {
        "nodes": [{"id": name, "label": name, "type": type} for name, type in nodes],
        "links": edges
    }


# ──────────────────────────────────────────────
# POST /api/test-resume — Live Demo (enriched)
# ──────────────────────────────────────────────

@app.post("/api/test-resume")
async def test_resume(file: UploadFile = File(...)):
    import PyPDF2
    import google.generativeai as genai
    from dotenv import load_dotenv
    import io

    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    llm_model = genai.GenerativeModel('gemini-flash-latest')

    # 1. Read the uploaded file
    content = await file.read()
    filename = file.filename or "resume.txt"

    if filename.lower().endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        text = text.strip()
    else:
        text = content.decode("utf-8", errors="ignore").strip()

    if not text:
        return {"error": "Could not extract any text from the uploaded file."}

    # 2. Use Gemini to extract skills
    prompt = f"""You are an expert technical recruiter AI. Extract all technical skills, programming languages, frameworks, and tools from the following resume.
Return ONLY a valid JSON array of lowercase strings. Example: ["python", "docker", "react"]
Do not include any markdown, explanation, or formatting — just the raw JSON array.

Resume:
{text[:4000]}
"""

    extracted_skills = []
    try:
        response = llm_model.generate_content(prompt)
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        extracted_skills = json.loads(cleaned)
    except Exception as e:
        return {"error": f"LLM skill extraction failed: {str(e)}"}

    if not extracted_skills:
        return {"error": "No skills could be extracted from this resume."}

    # 3. Score using DETAILED methods
    dataset = _load_dataset()
    jobs = dataset["jobs"]

    keyword_model = KeywordMatching()
    graph_model = GraphMatching()

    kw_results = []
    gr_results = []

    for job in jobs:
        req_skills = job["required_skills"]
        display_title = _clean_title(job["title"])

        kw_detail = keyword_model.get_detailed_score(extracted_skills, req_skills)
        gr_detail = graph_model.get_detailed_score(extracted_skills, req_skills)

        kw_results.append({
            "id": job["id"],
            "title": display_title,
            "required_skills": req_skills,
            **kw_detail
        })
        gr_results.append({
            "id": job["id"],
            "title": display_title,
            "required_skills": req_skills,
            **gr_detail
        })

    kw_ranked = sorted(kw_results, key=lambda x: x["score"], reverse=True)
    gr_ranked = sorted(gr_results, key=lambda x: x["score"], reverse=True)

    graph_model.close()

    return {
        "extracted_skills": extracted_skills,
        "keyword_recommendations": kw_ranked[:8],
        "graph_recommendations": gr_ranked[:8],
        "total_jobs_scored": len(jobs),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
