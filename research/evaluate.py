import json
import os
from .models import KeywordMatching, GraphMatching

def precision_at_k(recommended_jobs, relevant_jobs, k=3):
    """
    Computes Precision@K.
    recommended_jobs: list of job_ids sorted by recommendation score
    relevant_jobs: list of relevant job_ids (ground truth)
    """
    if not recommended_jobs:
        return 0.0
        
    top_k = recommended_jobs[:k]
    relevant_set = set(relevant_jobs)
    hits = sum(1 for job in top_k if job in relevant_set)
    return hits / k

def evaluate():
    data_path = os.path.join(os.path.dirname(__file__), "dataset.json")
    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    resumes = dataset["resumes"]
    jobs = dataset["jobs"]
    ground_truth = dataset["ground_truth"]

    keyword_model = KeywordMatching()
    graph_model = GraphMatching()

    k_val = 2
    keyword_precisions = []
    graph_precisions = []

    print(f"--- Starting Evaluation Pipeline (K={k_val}) ---\n")

    for candidate in resumes:
        c_id = candidate["id"]
        c_skills = candidate["skills"]
        relevant_jobs = ground_truth.get(c_id, [])

        # Score all jobs
        kw_scores = []
        gr_scores = []

        for job in jobs:
            j_id = job["id"]
            req_skills = job["required_skills"]

            kw_score = keyword_model.get_score(c_skills, req_skills)
            gr_score = graph_model.get_score(c_skills, req_skills)

            kw_scores.append((j_id, kw_score))
            gr_scores.append((j_id, gr_score))

        # Sort jobs by score descending
        kw_scores.sort(key=lambda x: x[1], reverse=True)
        gr_scores.sort(key=lambda x: x[1], reverse=True)

        kw_ranked = [x[0] for x in kw_scores]
        gr_ranked = [x[0] for x in gr_scores]

        kw_p = precision_at_k(kw_ranked, relevant_jobs, k=k_val)
        gr_p = precision_at_k(gr_ranked, relevant_jobs, k=k_val)

        keyword_precisions.append(kw_p)
        graph_precisions.append(gr_p)

        print(f"Candidate: {candidate['name']}")
        print(f"Skills: {c_skills}")
        print(f"Expected relevant jobs: {relevant_jobs}")
        print(f"Keyword Top {k_val}: {kw_ranked[:k_val]} | Precision@{k_val}: {kw_p:.2f}")
        print(f"Graph Top {k_val}:   {gr_ranked[:k_val]} | Precision@{k_val}: {gr_p:.2f}")
        print("-" * 50)

    # Summary
    avg_kw_p = sum(keyword_precisions) / len(keyword_precisions) if keyword_precisions else 0
    avg_gr_p = sum(graph_precisions) / len(graph_precisions) if graph_precisions else 0

    print("\n=== EVALUATION REPORT ===")
    print(f"Average Keyword Precision@{k_val}: {avg_kw_p:.3f}")
    print(f"Average Graph Precision@{k_val}:   {avg_gr_p:.3f}")

    if avg_gr_p > avg_kw_p:
        print("\n✅ Conclusion: The Graph-Based approach successfully outperforms Keyword-Matching by identifying semantic relationships between skills.")
    else:
        print("\n⚠️ Conclusion: The Graph-Based approach did not outperform Keyword-Matching on this dataset.")

    graph_model.close()

if __name__ == "__main__":
    evaluate()
