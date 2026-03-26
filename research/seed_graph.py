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
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password") # Default to 'password' as per your .env

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Define skills and their relationships
SKILLS = [
    "python", "sql", "api design", "django", "postgresql", 
    "html", "pandas", "numpy", "machine learning", "javascript", 
    "react", "node.js", "mongodb", "css", "deep learning", "performance tuning"
]

# (child, parent)
SUBSETS = [
    ("django", "python"),
    ("pandas", "python"),
    ("numpy", "python"),
    ("postgresql", "sql"),
    ("react", "javascript"),
    ("node.js", "javascript"),
    ("deep learning", "machine learning")
]

# (skill1, skill2, similarity)
RELATED = [
    ("html", "css", 0.9),
    ("javascript", "html", 0.7),
    ("python", "machine learning", 0.8),
    ("pandas", "numpy", 0.85),
    ("sql", "mongodb", 0.6),
    ("api design", "node.js", 0.8),
    ("api design", "python", 0.7),
    ("postgresql", "performance tuning", 0.8)
]

def seed_database():
    with driver.session() as session:
        print("Clearing existing graph...")
        session.run("MATCH (n) DETACH DELETE n")

        print("Seeding skills...")
        for skill in SKILLS:
            session.run("MERGE (s:Skill {name: $name})", name=skill)

        print("Seeding SUBSET_OF relationships...")
        for child, parent in SUBSETS:
            session.run('''
                MATCH (c:Skill {name: $child}), (p:Skill {name: $parent})
                MERGE (c)-[:SUBSET_OF]->(p)
            ''', child=child, parent=parent)

        print("Seeding RELATED_TO relationships...")
        for s1, s2, sim in RELATED:
            session.run('''
                MATCH (a:Skill {name: $s1}), (b:Skill {name: $s2})
                MERGE (a)-[:RELATED_TO {similarity: $sim}]->(b)
                MERGE (b)-[:RELATED_TO {similarity: $sim}]->(a)
            ''', s1=s1, s2=s2, sim=sim)

        print("Graph seeded successfully for research evaluation.")

if __name__ == "__main__":
    seed_database()
