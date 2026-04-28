import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

# Default to localhost for scripts running outside docker
NEO4J_URI = os.getenv("NEO4J_URI_HOST", os.getenv("NEO4J_URI", "bolt://localhost:7687"))
if "neo4j:7687" in NEO4J_URI: # Fix for when .env has docker internal address
    NEO4J_URI = NEO4J_URI.replace("neo4j:7687", "localhost:7687")

NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ─────────────────────────────────────────────────
# Comprehensive Skill Ontology for Dissertation
# ─────────────────────────────────────────────────

SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "r", "c++", "java", "go", "rust", "bash", "ruby",
    # Web Frontend
    "react", "angular", "vue", "next.js", "html", "html5", "css", "scss", "tailwind css",
    "redux", "webpack", "jest", "cypress", "styled components",
    # Web Backend
    "node.js", "django", "flask", "fastapi", "express", "spring boot",
    # Data Science & ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "pandas", "numpy", "tensorflow", "pytorch", "keras", "scikit-learn",
    "statistics", "data analysis", "data visualization", "predictive analytics",
    "reinforcement learning", "generative ai", "large language models",
    "computer vision", "neural networks",
    # Databases
    "sql", "postgresql", "mysql", "mongodb", "redis", "dynamodb", "elasticsearch",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "ci/cd", "jenkins", "github actions", "git",
    "ec2", "s3", "lambda", "cloudformation",
    # Cybersecurity
    "cybersecurity", "firewalls", "siem", "nist", "incident response",
    "vulnerability assessment", "penetration testing", "risk management",
    "network security", "encryption",
    # Data Engineering
    "apache spark", "kafka", "airflow", "etl", "data pipelines",
    "snowflake", "databricks", "hadoop",
    # General
    "api design", "restful apis", "microservices", "agile",
    "performance tuning", "linux", "windows server",
    "tcp/ip", "active directory", "vmware",
]

# (child, parent) — child is a specialization/subset of parent
SUBSETS = [
    # Python ecosystem
    ("django", "python"),
    ("flask", "python"),
    ("fastapi", "python"),
    ("pandas", "python"),
    ("numpy", "python"),
    ("scikit-learn", "python"),
    ("tensorflow", "python"),
    ("pytorch", "python"),
    ("keras", "python"),
    # JavaScript ecosystem
    ("react", "javascript"),
    ("angular", "javascript"),
    ("vue", "javascript"),
    ("node.js", "javascript"),
    ("next.js", "react"),
    ("redux", "react"),
    ("express", "node.js"),
    ("typescript", "javascript"),
    # SQL ecosystem
    ("postgresql", "sql"),
    ("mysql", "sql"),
    # ML hierarchy
    ("deep learning", "machine learning"),
    ("nlp", "machine learning"),
    ("natural language processing", "machine learning"),
    ("computer vision", "deep learning"),
    ("neural networks", "deep learning"),
    ("reinforcement learning", "machine learning"),
    ("generative ai", "deep learning"),
    ("large language models", "nlp"),
    ("predictive analytics", "machine learning"),
    # Cloud subsets
    ("ec2", "aws"),
    ("s3", "aws"),
    ("lambda", "aws"),
    ("cloudformation", "aws"),
    # DevOps subsets
    ("terraform", "ci/cd"),
    ("ansible", "ci/cd"),
    ("jenkins", "ci/cd"),
    ("github actions", "ci/cd"),
    ("docker", "ci/cd"),
    ("kubernetes", "docker"),
    # Web subsets
    ("html5", "html"),
    ("scss", "css"),
    ("tailwind css", "css"),
    # Security subsets
    ("penetration testing", "cybersecurity"),
    ("vulnerability assessment", "cybersecurity"),
    ("incident response", "cybersecurity"),
    ("network security", "cybersecurity"),
    ("encryption", "cybersecurity"),
    ("siem", "cybersecurity"),
    ("firewalls", "network security"),
    # Data Engineering subsets
    ("apache spark", "data pipelines"),
    ("kafka", "data pipelines"),
    ("airflow", "data pipelines"),
    ("etl", "data pipelines"),
]

# (skill1, skill2, similarity) — bidirectional semantic relationships
RELATED = [
    # Web relationships
    ("html", "css", 0.9),
    ("javascript", "html", 0.7),
    ("react", "redux", 0.85),
    ("react", "next.js", 0.9),
    ("node.js", "express", 0.9),
    ("api design", "restful apis", 0.95),
    ("api design", "node.js", 0.8),
    ("api design", "fastapi", 0.85),
    ("webpack", "javascript", 0.7),
    ("jest", "javascript", 0.7),
    ("cypress", "javascript", 0.65),
    # Backend relationships
    ("python", "api design", 0.7),
    ("django", "restful apis", 0.8),
    ("fastapi", "restful apis", 0.85),
    ("flask", "restful apis", 0.8),
    ("microservices", "docker", 0.75),
    ("microservices", "kubernetes", 0.8),
    ("microservices", "api design", 0.8),
    # Data Science relationships
    ("python", "machine learning", 0.8),
    ("pandas", "numpy", 0.85),
    ("pandas", "data analysis", 0.9),
    ("data analysis", "statistics", 0.85),
    ("data analysis", "data visualization", 0.8),
    ("tensorflow", "keras", 0.9),
    ("pytorch", "tensorflow", 0.85),
    ("scikit-learn", "statistics", 0.7),
    ("nlp", "natural language processing", 0.99),
    ("nlp", "large language models", 0.85),
    ("deep learning", "neural networks", 0.95),
    # Database relationships
    ("sql", "mongodb", 0.6),
    ("postgresql", "mysql", 0.85),
    ("postgresql", "performance tuning", 0.7),
    ("redis", "mongodb", 0.5),
    ("dynamodb", "mongodb", 0.6),
    ("elasticsearch", "mongodb", 0.5),
    # Cloud relationships
    ("aws", "azure", 0.8),
    ("aws", "gcp", 0.8),
    ("azure", "gcp", 0.8),
    ("docker", "kubernetes", 0.85),
    ("terraform", "cloudformation", 0.8),
    ("terraform", "ansible", 0.7),
    # DevOps relationships
    ("ci/cd", "git", 0.75),
    ("ci/cd", "agile", 0.6),
    ("jenkins", "github actions", 0.85),
    ("linux", "bash", 0.8),
    ("docker", "linux", 0.65),
    # Security relationships
    ("firewalls", "network security", 0.85),
    ("siem", "incident response", 0.8),
    ("nist", "risk management", 0.85),
    ("cybersecurity", "risk management", 0.75),
    ("penetration testing", "vulnerability assessment", 0.85),
    # Data Engineering relationships
    ("apache spark", "hadoop", 0.8),
    ("kafka", "data pipelines", 0.85),
    ("airflow", "etl", 0.85),
    ("snowflake", "sql", 0.7),
    ("databricks", "apache spark", 0.85),
    # Networking
    ("tcp/ip", "network security", 0.7),
    ("active directory", "windows server", 0.8),
    ("vmware", "linux", 0.5),
]

def seed_database():
    with driver.session() as session:
        print("Clearing existing graph...")
        session.run("MATCH (n) DETACH DELETE n")

        print(f"Seeding {len(SKILLS)} skills...")
        for skill in SKILLS:
            session.run("MERGE (s:Skill {name: $name})", name=skill)

        print(f"Seeding {len(SUBSETS)} SUBSET_OF relationships...")
        for child, parent in SUBSETS:
            session.run('''
                MATCH (c:Skill {name: $child}), (p:Skill {name: $parent})
                MERGE (c)-[:SUBSET_OF]->(p)
            ''', child=child, parent=parent)

        print(f"Seeding {len(RELATED)} RELATED_TO relationships...")
        for s1, s2, sim in RELATED:
            session.run('''
                MATCH (a:Skill {name: $s1}), (b:Skill {name: $s2})
                MERGE (a)-[:RELATED_TO {similarity: $sim}]->(b)
                MERGE (b)-[:RELATED_TO {similarity: $sim}]->(a)
            ''', s1=s1, s2=s2, sim=sim)

        # Print summary
        count = session.run("MATCH (n:Skill) RETURN count(n) AS c").single()["c"]
        rels = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        print(f"\n[OK] Graph seeded: {count} skills, {rels} relationships")

if __name__ == "__main__":
    seed_database()
