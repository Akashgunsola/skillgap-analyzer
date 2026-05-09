import spacy
from spacy.matcher import PhraseMatcher
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# We cache the nlp object and matcher to avoid loading them repeatedly
nlp = None
matcher = None

def init_spacy_extractor():
    global nlp, matcher
    if nlp is not None:
        return
    
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download as spacy_download
        spacy_download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    
    # Load skills from Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI_HOST", os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    if "neo4j:7687" in NEO4J_URI:
        NEO4J_URI = NEO4J_URI.replace("neo4j:7687", "localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    skills = []
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("MATCH (s:Skill) RETURN s.name AS name")
            skills = [record["name"].lower() for record in result]
        driver.close()
    except Exception as e:
        print("Could not load skills from Neo4j for spaCy:", e)
        
    if not skills:
        # Fallback to dataset file if neo4j is down
        print("Falling back to dataset json for skills...")
        import json
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "research", "dataset_real_with_ground_truth.json")
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                fallback_skills = set()
                for job in data.get("jobs", []):
                    for skill in job.get("required_skills", []):
                        fallback_skills.add(skill.lower())
                skills = list(fallback_skills)
        except Exception as e:
            print("Fallback also failed:", e)

    if skills:
        # Use nlp.pipe for efficiency when creating many docs
        patterns = list(nlp.pipe(skills))
        matcher.add("SKILLS", patterns)

def extract_skills_with_spacy(text: str) -> list:
    init_spacy_extractor()
    doc = nlp(text)
    matches = matcher(doc)
    extracted = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        extracted.add(span.text.lower())
    return list(extracted)
