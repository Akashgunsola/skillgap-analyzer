import spacy
from sentence_transformers import SentenceTransformer
from app.skills.loader import load_skills

# Load definitions
SKILL_MAP, ALIAS_MAP = load_skills()

# Initialize NLP Models
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model 'en_core_web_sm' is not installed. Run 'python -m spacy download en_core_web_sm'.")

# Add Entity Ruler
ruler = nlp.add_pipe("entity_ruler", before="ner")
patterns = []
for alias, skill_id in ALIAS_MAP.items():
    patterns.append({"label": "SKILL", "pattern": [{"LOWER": word} for word in alias.split()], "id": skill_id})
ruler.add_patterns(patterns)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_skills_and_embedding(text: str):
    doc = nlp(text)
    
    found = {}
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            skill_id = ent.ent_id_
            found[skill_id] = found.get(skill_id, 0) + 1
            
    # As per guide: Candidate Profile vector (averaging summary/skills)
    # We will embed the whole resume text for simplicity and performance
    profile_embedding = embedding_model.encode(text).tolist()
    
    return found, profile_embedding

