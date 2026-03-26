import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI_HOST", os.getenv("NEO4J_URI", "bolt://localhost:7687"))
if not os.getenv("DOCKER_ENV") and "neo4j:7687" in NEO4J_URI:
    NEO4J_URI = NEO4J_URI.replace("neo4j:7687", "localhost:7687")

NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password") # Default to 'password' as per your .env

class KeywordMatching:
    def __init__(self):
        pass

    def get_score(self, candidate_skills, job_requirements):
        """
        Computes score based on direct overlap.
        Score = len(intersection) / len(job_requirements)
        """
        if not job_requirements:
            return 0.0
            
        cand_set = set([s.lower() for s in candidate_skills])
        req_set = set([s.lower() for s in job_requirements])
        
        intersection = cand_set.intersection(req_set)
        return len(intersection) / len(req_set)

class GraphMatching:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def get_score(self, candidate_skills, job_requirements):
        """
        Computes score using Neo4j graph to find indirect matches via:
        - SUBSET_OF (child to parent = 1.0, parent to child = 0.5)
        - RELATED_TO (using similarity weight)
        """
        if not job_requirements:
            return 0.0

        query = '''
        WITH $candidate_skills AS cand_names, $required_skills AS req_names

        UNWIND req_names AS req_name
        MATCH (req:Skill {name: req_name})
        
        // Find best match among candidate skills for this requirement
        CALL {
            WITH req, cand_names
            UNWIND cand_names AS cand_name
            MATCH (cand:Skill {name: cand_name})
            
            OPTIONAL MATCH p1 = (cand)-[:SUBSET_OF*1..2]->(req)
            OPTIONAL MATCH p2 = (req)-[:SUBSET_OF*1..2]->(cand)
            OPTIONAL MATCH p3 = (cand)-[r:RELATED_TO]-(req)
            
            WITH cand, req,
                CASE
                    WHEN cand.name = req.name THEN 1.0
                    WHEN p1 IS NOT NULL THEN 1.0  // Candidate has specific skill (e.g. Django) for general req (Python)
                    WHEN p2 IS NOT NULL THEN 0.5  // Candidate has general skill (e.g. Python) for specific req (Django)
                    WHEN p3 IS NOT NULL THEN r.similarity
                    ELSE 0.0
                END AS match_score
                
            RETURN max(match_score) AS best_score
        }
        
        RETURN avg(best_score) AS final_score
        '''

        with self.driver.session() as session:
            result = session.run(
                query, 
                candidate_skills=[s.lower() for s in candidate_skills], 
                required_skills=[s.lower() for s in job_requirements]
            )
            record = result.single()
            if record and record["final_score"] is not None:
                return float(record["final_score"])
            return 0.0
                
    def close(self):
        self.driver.close()
