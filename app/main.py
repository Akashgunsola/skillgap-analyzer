import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from research.models import KeywordMatching, GraphMatching

app = FastAPI(title="Graph Job Recommendation Research API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def precision_at_k(recommended_jobs, relevant_jobs, k=3):
    if not recommended_jobs:
        return 0.0
    top_k = recommended_jobs[:k]
    relevant_set = set(relevant_jobs)
    hits = sum(1 for job in top_k if job in relevant_set)
    return hits / k

@app.get("/api/results")
async def get_results():
    data_path = os.path.join("research", "dataset.json")
    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    resumes = dataset["resumes"]
    jobs = dataset["jobs"]
    ground_truth = dataset["ground_truth"]

    keyword_model = KeywordMatching()
    graph_model = GraphMatching()

    k_val = 2
    results = []
    kw_precisions = []
    gr_precisions = []

    for candidate in resumes:
        c_id = candidate["id"]
        c_skills = candidate["skills"]
        relevant_jobs = ground_truth.get(c_id, [])

        kw_scores = []
        gr_scores = []

        for job in jobs:
            j_id = job["id"]
            req_skills = job["required_skills"]

            kw_score = keyword_model.get_score(c_skills, req_skills)
            gr_score = graph_model.get_score(c_skills, req_skills)

            kw_scores.append({"id": j_id, "title": job["title"], "score": kw_score})
            gr_scores.append({"id": j_id, "title": job["title"], "score": gr_score})

        kw_ranked = sorted(kw_scores, key=lambda x: x["score"], reverse=True)
        gr_ranked = sorted(gr_scores, key=lambda x: x["score"], reverse=True)

        kw_p = precision_at_k([r["id"] for r in kw_ranked], relevant_jobs, k=k_val)
        gr_p = precision_at_k([r["id"] for r in gr_ranked], relevant_jobs, k=k_val)

        kw_precisions.append(kw_p)
        gr_precisions.append(gr_p)

        results.append({
            "candidate": candidate["name"],
            "skills": c_skills,
            "relevant_jobs": relevant_jobs,
            "keyword_top": kw_ranked[:k_val],
            "graph_top": gr_ranked[:k_val],
            "keyword_precision": kw_p,
            "graph_precision": gr_p
        })

    avg_kw_p = sum(kw_precisions) / len(kw_precisions) if kw_precisions else 0
    avg_gr_p = sum(gr_precisions) / len(gr_precisions) if gr_precisions else 0

    return {
        "k": k_val,
        "avg_keyword_precision": avg_kw_p,
        "avg_graph_precision": avg_gr_p,
        "details": results
    }

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
                
    return {
        "nodes": [{"id": name, "label": name, "type": type} for name, type in nodes],
        "links": edges
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
