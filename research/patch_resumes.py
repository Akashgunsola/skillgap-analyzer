"""
Patch dataset_real.json:
1. Add the 7 new resumes (skills parsed directly - no Gemini needed)
2. Remove jobs with 0 extracted skills (rate limit failures)
"""
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(base_dir, "dataset_real.json")

with open(dataset_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)

# Check if new resumes already exist
existing_names = {r["name"] for r in dataset["resumes"]}

new_resumes = [
    {
        "id": "c_6",
        "name": "resume_mobile_developer",
        "skills": [
            "react native", "flutter", "swift", "swiftui", "kotlin",
            "jetpack compose", "ios development", "android development",
            "javascript", "typescript", "redux", "restful apis", "firebase",
            "git", "ci/cd", "unit testing"
        ]
    },
    {
        "id": "c_7",
        "name": "resume_java_backend",
        "skills": [
            "java", "spring boot", "hibernate", "jpa", "postgresql", "mysql",
            "microservices", "kafka", "rabbitmq", "docker", "kubernetes",
            "maven", "gradle", "restful apis", "graphql", "aws", "ci/cd",
            "git", "system design", "design patterns", "agile"
        ]
    },
    {
        "id": "c_8",
        "name": "resume_data_engineer",
        "skills": [
            "python", "sql", "apache spark", "airflow", "kafka", "etl",
            "data pipelines", "snowflake", "databricks", "dbt",
            "apache flink", "hadoop", "aws", "docker", "git",
            "data visualization", "postgresql"
        ]
    },
    {
        "id": "c_9",
        "name": "resume_ml_engineer",
        "skills": [
            "python", "pytorch", "tensorflow", "machine learning",
            "deep learning", "mlops", "mlflow", "computer vision", "nlp",
            "large language models", "generative ai", "neural networks",
            "docker", "kubernetes", "aws", "scikit-learn", "sql", "ci/cd",
            "data pipelines"
        ]
    },
    {
        "id": "c_10",
        "name": "resume_qa_automation",
        "skills": [
            "selenium", "playwright", "cypress", "jest", "python",
            "javascript", "typescript", "unit testing", "integration testing",
            "ci/cd", "jenkins", "github actions", "git", "docker", "react",
            "api testing"
        ]
    },
    {
        "id": "c_11",
        "name": "resume_data_analyst",
        "skills": [
            "sql", "python", "pandas", "data analysis", "statistics",
            "data visualization", "power bi", "tableau", "excel",
            "postgresql", "predictive analytics", "numpy", "jupyter"
        ]
    },
    {
        "id": "c_12",
        "name": "resume_go_devops",
        "skills": [
            "go", "docker", "kubernetes", "terraform", "helm", "prometheus",
            "grafana", "grpc", "restful apis", "microservices", "aws", "gcp",
            "linux", "bash", "python", "postgresql", "redis", "ci/cd",
            "github actions", "jenkins", "git", "system design"
        ]
    },
]

added = 0
for resume in new_resumes:
    if resume["name"] not in existing_names:
        dataset["resumes"].append(resume)
        added += 1
        print(f"  + Added {resume['name']} ({len(resume['skills'])} skills)")
    else:
        print(f"  = {resume['name']} already exists, skipping")

# Remove jobs with 0 skills
original_job_count = len(dataset["jobs"])
dataset["jobs"] = [j for j in dataset["jobs"] if j.get("required_skills")]
removed = original_job_count - len(dataset["jobs"])

with open(dataset_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2)

print(f"\nDone!")
print(f"  Resumes: {len(dataset['resumes'])} ({added} new)")
print(f"  Jobs: {len(dataset['jobs'])} ({removed} empty ones removed)")
print(f"\nNext: run 'python research/generate_ground_truth.py' (needs 12 API calls, run tomorrow)")
