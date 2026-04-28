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

    def get_detailed_score(self, candidate_skills, job_requirements):
        """
        Returns score plus matched/missing skill lists for explanation UI.
        """
        if not job_requirements:
            return {"score": 0.0, "matched": [], "missing": [], "match_ratio": "0/0"}

        cand_set = set([s.lower() for s in candidate_skills])
        req_set = set([s.lower() for s in job_requirements])

        matched = sorted(list(cand_set.intersection(req_set)))
        missing = sorted(list(req_set - cand_set))
        score = len(matched) / len(req_set) if req_set else 0.0

        return {
            "score": round(score, 4),
            "matched": matched,
            "missing": missing,
            "match_ratio": f"{len(matched)}/{len(req_set)}",
            "explanation": f"Matched {len(matched)} of {len(req_set)} required skills directly"
        }

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

    def get_detailed_score(self, candidate_skills, job_requirements):
        """
        Returns score + detailed graph path explanations for each requirement.
        Shows exactly HOW the graph connected candidate skills to job requirements.
        """
        if not job_requirements:
            return {"score": 0.0, "paths": [], "direct_matches": [], "graph_matches": [], "unmatched": [], "explanation": ""}

        query = '''
        WITH $candidate_skills AS cand_names, $required_skills AS req_names

        UNWIND req_names AS req_name
        OPTIONAL MATCH (req:Skill {name: req_name})
        
        CALL {
            WITH req, cand_names, req_name
            WITH req, cand_names, req_name
            WHERE req IS NOT NULL
            UNWIND cand_names AS cand_name
            MATCH (cand:Skill {name: cand_name})
            
            OPTIONAL MATCH p1 = (cand)-[:SUBSET_OF*1..2]->(req)
            OPTIONAL MATCH p2 = (req)-[:SUBSET_OF*1..2]->(cand)
            OPTIONAL MATCH p3 = (cand)-[r:RELATED_TO]-(req)
            
            WITH cand, req,
                CASE
                    WHEN cand.name = req.name THEN 1.0
                    WHEN p1 IS NOT NULL THEN 1.0
                    WHEN p2 IS NOT NULL THEN 0.5
                    WHEN p3 IS NOT NULL THEN r.similarity
                    ELSE 0.0
                END AS match_score,
                CASE
                    WHEN cand.name = req.name THEN 'direct'
                    WHEN p1 IS NOT NULL THEN 'subset_of'
                    WHEN p2 IS NOT NULL THEN 'parent_of'
                    WHEN p3 IS NOT NULL THEN 'related_to'
                    ELSE 'none'
                END AS match_type,
                CASE
                    WHEN p3 IS NOT NULL THEN r.similarity
                    ELSE null
                END AS similarity
                
            ORDER BY match_score DESC
            LIMIT 1
            RETURN cand.name AS matched_skill, match_score, match_type, similarity
        }
        
        RETURN req_name, 
               COALESCE(matched_skill, 'none') AS matched_skill,
               COALESCE(match_score, 0.0) AS score,
               COALESCE(match_type, 'none') AS match_type,
               similarity
        '''

        paths = []
        direct_matches = []
        graph_matches = []
        unmatched = []
        scores = []

        with self.driver.session() as session:
            result = session.run(
                query,
                candidate_skills=[s.lower() for s in candidate_skills],
                required_skills=[s.lower() for s in job_requirements]
            )
            for record in result:
                req = record["req_name"]
                skill = record["matched_skill"]
                score = float(record["score"])
                mtype = record["match_type"]
                sim = record["similarity"]
                scores.append(score)

                if mtype == "direct":
                    direct_matches.append(req)
                    paths.append({"req": req, "via": skill, "type": "direct", "label": f"{req} ✓ (exact match)", "score": score})
                elif mtype == "subset_of":
                    graph_matches.append(req)
                    paths.append({"req": req, "via": skill, "type": "subset_of", "label": f"{skill} → SUBSET_OF → {req}", "score": score})
                elif mtype == "parent_of":
                    graph_matches.append(req)
                    paths.append({"req": req, "via": skill, "type": "parent_of", "label": f"{req} → SUBSET_OF → {skill}", "score": score})
                elif mtype == "related_to":
                    graph_matches.append(req)
                    sim_pct = int((sim or 0) * 100)
                    paths.append({"req": req, "via": skill, "type": "related_to", "label": f"{skill} ↔ RELATED_TO ↔ {req} ({sim_pct}%)", "score": score})
                else:
                    unmatched.append(req)
                    paths.append({"req": req, "via": "none", "type": "none", "label": f"{req} ✗ (no graph connection)", "score": 0.0})

        final_score = sum(scores) / len(scores) if scores else 0.0
        graph_only = len(graph_matches)

        explanation = f"Found {len(direct_matches)} direct + {graph_only} graph-connected matches across {len(job_requirements)} requirements"

        return {
            "score": round(final_score, 4),
            "paths": paths,
            "direct_matches": direct_matches,
            "graph_matches": graph_matches,
            "unmatched": unmatched,
            "explanation": explanation
        }
                
    def close(self):
        self.driver.close()
