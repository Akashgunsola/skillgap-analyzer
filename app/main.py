import os
import sys
import json
import threading
from datetime import datetime
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

# Add the project root to sys.path so we can import research modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research.models import KeywordMatching, GraphMatching
from research.ontology_expander import (
    get_existing_skills, find_new_skills, classify_new_skills,
    merge_into_graph, log_expansion, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
)

app = FastAPI(title="Recommendation System — Graph Traversal & AI")

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
# Usage log — persists across requests
# ──────────────────────────────────────────────

USAGE_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "data", "usage_log.json")

def _load_usage_log():
    """Load the usage log from disk."""
    if os.path.exists(USAGE_LOG_PATH):
        try:
            with open(USAGE_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def _save_usage_log(log):
    """Save the usage log to disk."""
    os.makedirs(os.path.dirname(USAGE_LOG_PATH), exist_ok=True)
    with open(USAGE_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

def _append_session(session_data):
    """Append a single session to the usage log."""
    log = _load_usage_log()
    log.append(session_data)
    _save_usage_log(log)


def _background_expand_ontology(new_skills_list):
    """
    Run ontology expansion in a background thread so the API response
    is not delayed. New skills discovered from resumes/jobs are classified
    via Gemini and merged into Neo4j automatically.
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        existing = get_existing_skills(driver)
        genuinely_new = find_new_skills(set(new_skills_list), existing)

        if genuinely_new:
            print(f"[Ontology Expander] Found {len(genuinely_new)} new skills, classifying...")
            classifications = classify_new_skills(genuinely_new, existing)
            stats = merge_into_graph(driver, classifications, existing)
            log_expansion(classifications, stats, "auto_resume_upload")
            print(f"[Ontology Expander] Added {stats['nodes_added']} nodes, "
                  f"{stats['subset_edges']} subset edges, {stats['related_edges']} related edges")
        else:
            print("[Ontology Expander] No new skills to add.")

        driver.close()
    except Exception as e:
        print(f"[Ontology Expander] Background expansion failed: {e}")


# ──────────────────────────────────────────────
# GET /api/metrics — Aggregated from real usage
# ──────────────────────────────────────────────

@app.get("/api/metrics")
async def get_metrics():
    """Aggregate metrics across all users who have uploaded resumes."""
    log = _load_usage_log()

    if not log:
        return {
            "k": 5,
            "candidates": 0,
            "total_jobs": 0,
            "avg_keyword_score": 0,
            "avg_graph_score": 0,
            "precision": {"keyword": 0, "graph": 0},
            "recall": {"keyword": 0, "graph": 0},
            "diversity": {"keyword": 0, "graph": 0},
            "novelty": {"graph_only_count": 0, "description": "No resumes analyzed yet"},
            "empty": True
        }

    k_val = 5
    kw_avg_scores = []
    gr_avg_scores = []
    kw_all_recs = set()
    gr_all_recs = set()
    graph_only_jobs = set()
    total_kw_matched = 0
    total_kw_required = 0
    total_gr_connected = 0
    total_gr_required = 0

    for session in log:
        kw_recs = session.get("keyword_top_ids", [])
        gr_recs = session.get("graph_top_ids", [])
        kw_scores = session.get("keyword_scores", [])
        gr_scores = session.get("graph_scores", [])

        if kw_scores:
            kw_avg_scores.append(sum(kw_scores) / len(kw_scores))
        if gr_scores:
            gr_avg_scores.append(sum(gr_scores) / len(gr_scores))

        kw_all_recs.update(kw_recs[:k_val])
        gr_all_recs.update(gr_recs[:k_val])
        graph_only_jobs.update(set(gr_recs[:k_val]) - set(kw_recs[:k_val]))

        total_kw_matched += session.get("total_kw_matched", 0)
        total_kw_required += session.get("total_kw_required", 0)
        total_gr_connected += session.get("total_gr_connected", 0)
        total_gr_required += session.get("total_gr_required", 0)

    avg = lambda lst: sum(lst) / len(lst) if lst else 0

    # Precision = avg of top-K scores (how relevant are the top recommendations)
    kw_precision = round(avg(kw_avg_scores) * 100, 1)
    gr_precision = round(avg(gr_avg_scores) * 100, 1)

    # Recall = overall skill coverage (matched/required across all sessions)
    kw_recall = round((total_kw_matched / total_kw_required * 100) if total_kw_required else 0, 1)
    gr_recall = round((total_gr_connected / total_gr_required * 100) if total_gr_required else 0, 1)

    return {
        "k": k_val,
        "candidates": len(log),
        "total_jobs": log[0].get("total_jobs", 0) if log else 0,
        "avg_keyword_score": round(avg(kw_avg_scores) * 100, 1),
        "avg_graph_score": round(avg(gr_avg_scores) * 100, 1),
        "precision": {
            "keyword": kw_precision,
            "graph": gr_precision,
        },
        "recall": {
            "keyword": kw_recall,
            "graph": gr_recall,
        },
        "diversity": {
            "keyword": len(kw_all_recs),
            "graph": len(gr_all_recs),
        },
        "novelty": {
            "graph_only_count": len(graph_only_jobs),
            "description": f"Graph discovered {len(graph_only_jobs)} unique jobs that keyword matching missed"
        },
        "empty": False
    }


@app.delete("/api/metrics")
async def reset_metrics():
    """Clear the usage log."""
    _save_usage_log([])
    return {"status": "cleared"}


# ──────────────────────────────────────────────
# GET /api/history — Full candidate history
# ──────────────────────────────────────────────

@app.get("/api/history")
async def get_history():
    """Return all past candidate sessions with full data."""
    log = _load_usage_log()
    # Return in reverse chronological order (newest first)
    return {"sessions": list(reversed(log)), "total": len(log)}


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
# GET /api/traversal-graph/:job_index
# Returns the mini-graph for a specific job recommendation
# showing how candidate skills connect to job requirements
# ──────────────────────────────────────────────

@app.post("/api/traversal-graph")
async def get_traversal_graph(payload: dict):
    """
    Given candidate skills and a job's required skills + paths data,
    query Neo4j for the actual subgraph connecting them.
    Returns nodes and edges for interactive visualization.
    """
    candidate_skills = [s.lower() for s in payload.get("candidate_skills", [])]
    required_skills = [s.lower() for s in payload.get("required_skills", [])]
    paths_data = payload.get("paths", [])

    graph_model = GraphMatching()

    # Collect all relevant skill names for the subgraph
    all_skill_names = set(candidate_skills) | set(required_skills)

    # Also add intermediate skills from paths
    for p in paths_data:
        if p.get("via") and p["via"] != "none":
            all_skill_names.add(p["via"].lower())

    # Query Neo4j for edges between all these skills
    query = """
    WITH $skills AS skill_names
    UNWIND skill_names AS s1
    UNWIND skill_names AS s2
    WITH s1, s2 WHERE s1 < s2
    OPTIONAL MATCH (a:Skill {name: s1})-[r]->(b:Skill {name: s2})
    OPTIONAL MATCH (b2:Skill {name: s2})-[r2]->(a2:Skill {name: s1})
    WITH s1, s2, 
         CASE WHEN r IS NOT NULL THEN type(r) ELSE null END AS fwd_type,
         CASE WHEN r IS NOT NULL AND type(r) = 'RELATED_TO' THEN r.similarity ELSE null END AS fwd_sim,
         CASE WHEN r2 IS NOT NULL THEN type(r2) ELSE null END AS bwd_type,
         CASE WHEN r2 IS NOT NULL AND type(r2) = 'RELATED_TO' THEN r2.similarity ELSE null END AS bwd_sim
    WHERE fwd_type IS NOT NULL OR bwd_type IS NOT NULL
    RETURN s1, s2, fwd_type, fwd_sim, bwd_type, bwd_sim
    """

    nodes = []
    edges = []
    seen_edges = set()

    with graph_model.driver.session() as session:
        result = session.run(query, skills=list(all_skill_names))
        for record in result:
            s1 = record["s1"]
            s2 = record["s2"]
            fwd_type = record["fwd_type"]
            fwd_sim = record["fwd_sim"]
            bwd_type = record["bwd_type"]
            bwd_sim = record["bwd_sim"]

            if fwd_type:
                edge_key = (s1, s2, fwd_type)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edge = {"source": s1, "target": s2, "type": fwd_type}
                    if fwd_sim is not None:
                        edge["similarity"] = fwd_sim
                    edges.append(edge)

            if bwd_type:
                edge_key = (s2, s1, bwd_type)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edge = {"source": s2, "target": s1, "type": bwd_type}
                    if bwd_sim is not None:
                        edge["similarity"] = bwd_sim
                    edges.append(edge)

    graph_model.close()

    # Build nodes with categories
    cand_set = set(candidate_skills)
    req_set = set(required_skills)
    
    for skill in all_skill_names:
        node_type = "both" if skill in cand_set and skill in req_set else \
                    "candidate" if skill in cand_set else \
                    "required" if skill in req_set else "intermediate"
        nodes.append({"id": skill, "label": skill, "type": node_type})

    return {
        "nodes": nodes,
        "edges": edges,
        "paths": paths_data
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

    # 4. Log this session for aggregate metrics
    kw_top_8 = kw_ranked[:8]
    gr_top_8 = gr_ranked[:8]

    total_kw_matched = sum(len(j.get("matched", [])) for j in kw_top_8)
    total_kw_required = sum(len(j.get("required_skills", [])) for j in kw_top_8)
    total_gr_connected = sum(len(j.get("direct_matches", [])) + len(j.get("graph_matches", [])) for j in gr_top_8)
    total_gr_required = sum(len(j.get("required_skills", [])) for j in gr_top_8)

    _append_session({
        "filename": filename,
        "timestamp": datetime.now().isoformat(),
        "skills": extracted_skills,
        "keyword_recommendations": kw_top_8,
        "graph_recommendations": gr_top_8,
        "keyword_top_ids": [j["id"] for j in kw_top_8],
        "graph_top_ids": [j["id"] for j in gr_top_8],
        "keyword_scores": [j["score"] for j in kw_top_8],
        "graph_scores": [j["score"] for j in gr_top_8],
        "total_kw_matched": total_kw_matched,
        "total_kw_required": total_kw_required,
        "total_gr_connected": total_gr_connected,
        "total_gr_required": total_gr_required,
        "total_jobs": len(jobs),
    })

    # 5. Trigger background ontology expansion with newly discovered skills
    threading.Thread(
        target=_background_expand_ontology,
        args=(extracted_skills,),
        daemon=True
    ).start()

    return {
        "extracted_skills": extracted_skills,
        "keyword_recommendations": kw_top_8,
        "graph_recommendations": gr_top_8,
        "total_jobs_scored": len(jobs),
    }


# ──────────────────────────────────────────────
# POST /api/expand-ontology — Manual trigger
# ──────────────────────────────────────────────

@app.post("/api/expand-ontology")
async def expand_ontology_endpoint():
    """
    Manually trigger ontology expansion by scanning all data sources
    (datasets + usage log) for skills not yet in the graph.
    """
    from neo4j import GraphDatabase as GD
    driver = GD.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    existing = get_existing_skills(driver)
    before_count = len(existing)

    # Collect from all sources
    from research.ontology_expander import collect_skills_from_dataset, collect_skills_from_usage_log
    discovered = collect_skills_from_dataset() | collect_skills_from_usage_log()
    genuinely_new = find_new_skills(discovered, existing)

    if not genuinely_new:
        driver.close()
        return {"status": "up_to_date", "message": "No new skills found", "total_skills": before_count}

    classifications = classify_new_skills(genuinely_new, existing)
    stats = merge_into_graph(driver, classifications, existing)
    log_expansion(classifications, stats, "manual_api_trigger")

    after_count = len(get_existing_skills(driver))
    driver.close()

    return {
        "status": "expanded",
        "new_skills": sorted(genuinely_new),
        "stats": stats,
        "before": before_count,
        "after": after_count,
    }


# ──────────────────────────────────────────────
# GET /api/ontology-log — View expansion history
# ──────────────────────────────────────────────

@app.get("/api/ontology-log")
async def get_ontology_log():
    """Return the full ontology expansion audit log."""
    if os.path.exists(EXPANSION_LOG_PATH):
        with open(EXPANSION_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


EXPANSION_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "data", "ontology_expansions.json")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
