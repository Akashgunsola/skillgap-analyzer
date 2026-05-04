"""
Expand the dataset with 30 new jobs covering diverse tech domains.
This adds to dataset_real_with_ground_truth.json directly.
"""
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(base_dir, "dataset_real_with_ground_truth.json")

with open(dataset_path, "r", encoding="utf-8") as f:
    dataset = json.load(f)

NEW_JOBS = [
    # ── Mobile Development ──
    {
        "id": "j_51", "title": "Senior_iOS_Engineer_Swift_SwiftUI",
        "required_skills": ["swift", "swiftui", "ios development", "git", "ci/cd", "unit testing", "restful apis", "agile"]
    },
    {
        "id": "j_52", "title": "Android_Developer_Kotlin_Jetpack",
        "required_skills": ["kotlin", "jetpack compose", "android development", "git", "firebase", "restful apis", "gradle", "unit testing"]
    },
    {
        "id": "j_53", "title": "Cross_Platform_Mobile_Engineer_React_Native",
        "required_skills": ["react native", "javascript", "typescript", "redux", "restful apis", "git", "ios development", "android development"]
    },
    {
        "id": "j_54", "title": "Flutter_Mobile_Developer",
        "required_skills": ["flutter", "ios development", "android development", "firebase", "restful apis", "git", "ci/cd", "agile"]
    },
    # ── Java / Spring Backend ──
    {
        "id": "j_55", "title": "Senior_Java_Backend_Engineer_Spring_Boot",
        "required_skills": ["java", "spring boot", "hibernate", "postgresql", "docker", "kubernetes", "microservices", "restful apis", "maven", "ci/cd", "aws"]
    },
    {
        "id": "j_56", "title": "Java_Microservices_Architect",
        "required_skills": ["java", "spring boot", "microservices", "kafka", "docker", "kubernetes", "api design", "postgresql", "redis", "graphql", "system design"]
    },
    # ── Go / Rust Systems ──
    {
        "id": "j_57", "title": "Go_Backend_Engineer_Distributed_Systems",
        "required_skills": ["go", "docker", "kubernetes", "grpc", "postgresql", "redis", "kafka", "microservices", "linux", "git", "ci/cd"]
    },
    {
        "id": "j_58", "title": "Rust_Systems_Engineer",
        "required_skills": ["rust", "c++", "linux", "system design", "performance tuning", "docker", "git"]
    },
    # ── Full Stack ──
    {
        "id": "j_59", "title": "Fullstack_Engineer_Next_js_Node_GraphQL",
        "required_skills": ["next.js", "react", "typescript", "node.js", "graphql", "postgresql", "docker", "git", "tailwind css", "aws"]
    },
    {
        "id": "j_60", "title": "MERN_Stack_Developer",
        "required_skills": ["react", "node.js", "express", "mongodb", "javascript", "typescript", "redux", "restful apis", "git", "docker"]
    },
    {
        "id": "j_61", "title": "Angular_Fullstack_Developer_Java_Spring",
        "required_skills": ["angular", "java", "spring boot", "typescript", "postgresql", "restful apis", "docker", "git", "jenkins"]
    },
    # ── Data Engineering ──
    {
        "id": "j_62", "title": "Senior_Data_Engineer_Spark_Airflow",
        "required_skills": ["python", "apache spark", "airflow", "sql", "kafka", "data pipelines", "aws", "docker", "etl", "snowflake"]
    },
    {
        "id": "j_63", "title": "Data_Engineer_Databricks_dbt",
        "required_skills": ["python", "sql", "databricks", "dbt", "snowflake", "etl", "data pipelines", "aws", "apache spark", "git"]
    },
    {
        "id": "j_64", "title": "Streaming_Data_Engineer_Kafka_Flink",
        "required_skills": ["kafka", "apache flink", "python", "java", "data pipelines", "docker", "kubernetes", "sql", "aws", "elasticsearch"]
    },
    # ── ML Engineering / MLOps ──
    {
        "id": "j_65", "title": "ML_Engineer_PyTorch_MLOps",
        "required_skills": ["python", "pytorch", "machine learning", "mlops", "mlflow", "docker", "kubernetes", "aws", "sql", "deep learning"]
    },
    {
        "id": "j_66", "title": "Computer_Vision_Engineer",
        "required_skills": ["python", "computer vision", "deep learning", "pytorch", "tensorflow", "c++", "docker", "linux", "neural networks"]
    },
    {
        "id": "j_67", "title": "NLP_Engineer_LLM_Fine_Tuning",
        "required_skills": ["python", "nlp", "large language models", "pytorch", "generative ai", "docker", "aws", "sql", "data pipelines"]
    },
    # ── QA / Testing ──
    {
        "id": "j_68", "title": "QA_Automation_Engineer_Selenium_Playwright",
        "required_skills": ["selenium", "playwright", "python", "javascript", "unit testing", "integration testing", "ci/cd", "git", "docker"]
    },
    {
        "id": "j_69", "title": "SDET_Engineer_Cypress_Jest",
        "required_skills": ["cypress", "jest", "javascript", "typescript", "react", "unit testing", "integration testing", "git", "ci/cd"]
    },
    # ── Blockchain / Web3 ──
    {
        "id": "j_70", "title": "Blockchain_Developer_Solidity_Ethereum",
        "required_skills": ["solidity", "ethereum", "smart contracts", "web3", "javascript", "typescript", "node.js", "git"]
    },
    {
        "id": "j_71", "title": "Web3_Fullstack_Developer",
        "required_skills": ["web3", "react", "typescript", "solidity", "ethereum", "node.js", "graphql", "git", "blockchain"]
    },
    # ── IoT / Embedded ──
    {
        "id": "j_72", "title": "IoT_Engineer_Python_MQTT",
        "required_skills": ["iot", "mqtt", "python", "raspberry pi", "docker", "aws", "linux", "embedded systems", "sql"]
    },
    {
        "id": "j_73", "title": "Embedded_Systems_Engineer_C_Plus_Plus",
        "required_skills": ["c++", "embedded systems", "linux", "arduino", "raspberry pi", "iot", "git", "python"]
    },
    # ── Cloud Architecture ──
    {
        "id": "j_74", "title": "AWS_Solutions_Architect",
        "required_skills": ["aws", "ec2", "s3", "lambda", "cloudformation", "terraform", "docker", "kubernetes", "ci/cd", "python", "system design"]
    },
    {
        "id": "j_75", "title": "Azure_Cloud_Engineer",
        "required_skills": ["azure", "terraform", "docker", "kubernetes", "ci/cd", "python", "linux", "git", "helm", "prometheus"]
    },
    {
        "id": "j_76", "title": "GCP_Data_Cloud_Architect",
        "required_skills": ["gcp", "python", "sql", "apache spark", "data pipelines", "docker", "kubernetes", "terraform", "airflow"]
    },
    # ── Site Reliability / Platform ──
    {
        "id": "j_77", "title": "SRE_Engineer_Kubernetes_Prometheus",
        "required_skills": ["kubernetes", "docker", "prometheus", "grafana", "terraform", "linux", "python", "bash", "ci/cd", "helm", "aws"]
    },
    {
        "id": "j_78", "title": "Platform_Engineer_Infrastructure",
        "required_skills": ["kubernetes", "terraform", "docker", "github actions", "python", "go", "linux", "aws", "helm", "ci/cd"]
    },
    # ── Svelte / Vue Frontend ──
    {
        "id": "j_79", "title": "Vue_js_Frontend_Engineer",
        "required_skills": ["vue", "javascript", "typescript", "html", "css", "tailwind css", "restful apis", "git", "jest"]
    },
    {
        "id": "j_80", "title": "Svelte_Frontend_Developer",
        "required_skills": ["svelte", "javascript", "typescript", "css", "html", "tailwind css", "restful apis", "git"]
    },
]

# Add new jobs to dataset
dataset["jobs"].extend(NEW_JOBS)

# Update ground truth for existing resumes based on new jobs
# c_1: Data Scientist (python, ML, pandas, tensorflow, etc)
dataset["ground_truth"]["c_1"].extend(["j_62", "j_63", "j_65", "j_66", "j_67"])

# c_2: Deep Learning Researcher (pytorch, DL, neural nets, LLMs, etc)
dataset["ground_truth"]["c_2"].extend(["j_65", "j_66", "j_67"])

# c_3: Fullstack Cloud (python, django, react, node, AWS, docker, etc)
dataset["ground_truth"]["c_3"].extend(["j_55", "j_59", "j_60", "j_62", "j_74", "j_77", "j_78"])

# c_4: Network Admin (tcp/ip, firewalls, vmware, windows server, etc) — few matches
# c_4 is already sparse, new jobs don't match well

# c_5: Frontend (JS, TS, React, Next.js, Redux, etc)
dataset["ground_truth"]["c_5"].extend(["j_53", "j_59", "j_60", "j_69", "j_71", "j_79", "j_80"])

# Save
with open(dataset_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2)

print(f"[OK] Dataset expanded to {len(dataset['jobs'])} jobs")
print(f"  New jobs added: j_51 through j_80 (30 jobs)")
print(f"  Domains: Mobile, Java/Spring, Go/Rust, Fullstack, Data Engineering,")
print(f"           ML/MLOps, QA/Testing, Blockchain, IoT, Cloud, SRE, Vue/Svelte")
