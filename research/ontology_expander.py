"""
Ontology Auto-Expander
──────────────────────
Automatically discovers new skills from job descriptions and resumes,
classifies them using Gemini LLM, and merges them into the Neo4j graph
with proper SUBSET_OF and RELATED_TO relationships.

Usage:
    python research/ontology_expander.py                    # scan data/ folder
    python research/ontology_expander.py --dry-run          # preview without writing to Neo4j
    python research/ontology_expander.py --from-text "..."  # discover from raw text
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

NEO4J_URI = os.getenv("NEO4J_URI_HOST", os.getenv("NEO4J_URI", "bolt://localhost:7687"))
if "neo4j:7687" in NEO4J_URI:
    NEO4J_URI = NEO4J_URI.replace("neo4j:7687", "localhost:7687")

NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPANSION_LOG_PATH = os.path.join(BASE_DIR, "data", "ontology_expansions.json")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel('gemini-flash-latest')


# ─────────────────────────────────────────────
# Step 1: Get Current Graph State
# ─────────────────────────────────────────────

def get_existing_skills(driver):
    """Fetch all skill names currently in the Neo4j graph."""
    with driver.session() as session:
        result = session.run("MATCH (s:Skill) RETURN s.name AS name")
        return set(record["name"] for record in result)


def get_existing_relationships(driver):
    """Fetch all existing edges (SUBSET_OF and RELATED_TO) from the graph."""
    subsets = []
    related = []
    with driver.session() as session:
        # Fetch SUBSET_OF edges
        result = session.run("""
            MATCH (c:Skill)-[:SUBSET_OF]->(p:Skill)
            RETURN c.name AS child, p.name AS parent
        """)
        for record in result:
            subsets.append((record["child"], record["parent"]))

        # Fetch RELATED_TO edges (one direction only to avoid duplicates)
        result = session.run("""
            MATCH (a:Skill)-[r:RELATED_TO]->(b:Skill)
            WHERE a.name < b.name
            RETURN a.name AS s1, b.name AS s2, r.similarity AS sim
        """)
        for record in result:
            related.append((record["s1"], record["s2"], record["sim"]))

    return subsets, related


# ─────────────────────────────────────────────
# Step 2: Discover New Skills from Data Sources
# ─────────────────────────────────────────────

def collect_skills_from_dataset():
    """Gather all skills mentioned in the existing dataset JSON files."""
    all_skills = set()

    for filename in ["dataset_real.json", "dataset_real_with_ground_truth.json"]:
        path = os.path.join(BASE_DIR, "research", filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for resume in data.get("resumes", []):
                all_skills.update(s.lower() for s in resume.get("skills", []))
            for job in data.get("jobs", []):
                all_skills.update(s.lower() for s in job.get("required_skills", []))

    return all_skills


def collect_skills_from_usage_log():
    """Gather skills from user resume uploads (usage_log.json)."""
    all_skills = set()
    log_path = os.path.join(BASE_DIR, "data", "usage_log.json")

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log = json.load(f)
        for session in log:
            all_skills.update(s.lower() for s in session.get("skills", []))

    return all_skills


def extract_skills_from_text(text):
    """Use Gemini to extract skills from arbitrary text."""
    prompt = f"""You are an expert technical recruiter AI. Extract all technical skills,
programming languages, frameworks, tools, and methodologies from the following text.
Return ONLY a valid JSON array of lowercase strings.
Example: ["python", "docker", "react", "agile"]
Do not include any markdown, explanation, or formatting — just the raw JSON array.

Text:
{text[:5000]}
"""
    try:
        response = llm.generate_content(prompt)
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        return set(json.loads(cleaned))
    except Exception as e:
        print(f"  [!] Skill extraction failed: {e}")
        return set()


def find_new_skills(discovered_skills, existing_skills):
    """Find skills that exist in data but NOT in the graph."""
    # Normalize everything to lowercase
    existing_lower = set(s.lower() for s in existing_skills)
    new_skills = set()

    for skill in discovered_skills:
        skill_lower = skill.lower().strip()
        if skill_lower and skill_lower not in existing_lower and len(skill_lower) > 1:
            new_skills.add(skill_lower)

    return new_skills


# ─────────────────────────────────────────────
# Step 3: Classify New Skills with LLM
# ─────────────────────────────────────────────

def classify_new_skills(new_skills, existing_skills):
    """
    Ask Gemini to classify each new skill:
    - What category/parent it belongs to (for SUBSET_OF)
    - What existing skills it's related to (for RELATED_TO)
    
    Returns a list of skill classification dicts.
    """
    if not new_skills:
        return []

    # Build a compact list of existing skills for context
    existing_list = sorted(existing_skills)

    # Process in batches of 15 to avoid token limits
    new_list = sorted(new_skills)
    all_classifications = []
    batch_size = 15

    for i in range(0, len(new_list), batch_size):
        batch = new_list[i:i + batch_size]
        print(f"  Classifying batch {i // batch_size + 1} ({len(batch)} skills)...")

        prompt = f"""You are a skill ontology expert. I have a knowledge graph of technical skills.

EXISTING SKILLS in the graph:
{json.dumps(existing_list)}

NEW SKILLS to classify:
{json.dumps(batch)}

For EACH new skill, determine:
1. "parent": The SINGLE most appropriate existing skill it is a specialization/subset of.
   - If the new skill is a framework/library of a language, the parent is that language.
   - If no good parent exists among the existing skills, set parent to null.
2. "related": A list of 1-5 existing skills that are semantically related (NOT parent/child).
   Each entry should have the skill name and a similarity score (0.0 to 1.0).
3. "category": A human-readable category label (e.g., "Programming Language", "ML Framework", "Cloud Service").

Return ONLY a valid JSON array. Example:
[
  {{
    "skill": "fastapi",
    "parent": "python",
    "related": [{{"skill": "flask", "similarity": 0.85}}, {{"skill": "restful apis", "similarity": 0.8}}],
    "category": "Web Framework"
  }}
]

Do not include any markdown blocks or explanations, just the raw JSON array.
"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = llm.generate_content(prompt)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                batch_result = json.loads(cleaned)
                all_classifications.extend(batch_result)
                time.sleep(3)  # Rate limit safety
                break
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg:
                    print(f"    [Rate Limit] Waiting 20 seconds...")
                    time.sleep(20)
                else:
                    print(f"    [Error] Attempt {attempt + 1}: {e}")
                    time.sleep(5)

    return all_classifications


# ─────────────────────────────────────────────
# Step 4: Merge Into Neo4j
# ─────────────────────────────────────────────

def merge_into_graph(driver, classifications, existing_skills):
    """Write classified skills and their relationships into Neo4j."""
    existing_lower = set(s.lower() for s in existing_skills)
    stats = {"nodes_added": 0, "subset_edges": 0, "related_edges": 0, "skipped": 0}

    with driver.session() as session:
        for entry in classifications:
            skill = entry.get("skill", "").lower().strip()
            parent = entry.get("parent")
            related_list = entry.get("related", [])
            category = entry.get("category", "Unknown")

            if not skill:
                continue

            # Create the skill node
            session.run(
                "MERGE (s:Skill {name: $name}) SET s.category = $category, s.auto_added = true, s.added_at = $ts",
                name=skill, category=category, ts=datetime.now().isoformat()
            )
            stats["nodes_added"] += 1

            # Create SUBSET_OF edge if parent exists in graph
            if parent and parent.lower() in existing_lower:
                session.run("""
                    MATCH (c:Skill {name: $child}), (p:Skill {name: $parent})
                    MERGE (c)-[:SUBSET_OF]->(p)
                """, child=skill, parent=parent.lower())
                stats["subset_edges"] += 1
            elif parent:
                print(f"    [Skip] Parent '{parent}' not in graph for '{skill}'")
                stats["skipped"] += 1

            # Create RELATED_TO edges
            for rel in related_list:
                rel_skill = rel.get("skill", "").lower()
                similarity = rel.get("similarity", 0.5)

                if rel_skill in existing_lower or rel_skill == skill:
                    if rel_skill != skill:  # Don't self-link
                        session.run("""
                            MATCH (a:Skill {name: $s1}), (b:Skill {name: $s2})
                            MERGE (a)-[:RELATED_TO {similarity: $sim}]->(b)
                            MERGE (b)-[:RELATED_TO {similarity: $sim}]->(a)
                        """, s1=skill, s2=rel_skill, sim=similarity)
                        stats["related_edges"] += 1

    return stats


# ─────────────────────────────────────────────
# Step 5: Logging
# ─────────────────────────────────────────────

def log_expansion(classifications, stats, source):
    """Append this expansion run to the audit log."""
    os.makedirs(os.path.dirname(EXPANSION_LOG_PATH), exist_ok=True)

    log = []
    if os.path.exists(EXPANSION_LOG_PATH):
        try:
            with open(EXPANSION_LOG_PATH, "r", encoding="utf-8") as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []

    log.append({
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "skills_classified": len(classifications),
        "stats": stats,
        "details": classifications
    })

    with open(EXPANSION_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)


# ─────────────────────────────────────────────
# Main Runner
# ─────────────────────────────────────────────

def expand_ontology(dry_run=False, from_text=None):
    """Main pipeline: discover → classify → merge → log."""

    print("=" * 60)
    print("  SKILL ONTOLOGY AUTO-EXPANDER")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    # 1. Get current graph state
    print("\n[1/5] Fetching current graph state...")
    existing_skills = get_existing_skills(driver)
    print(f"  Found {len(existing_skills)} skills in Neo4j")

    # 2. Discover skills from all sources
    print("\n[2/5] Discovering skills from data sources...")
    discovered = set()

    if from_text:
        print("  Extracting from provided text...")
        discovered = extract_skills_from_text(from_text)
        source = "manual_text"
    else:
        # Scan dataset files
        ds_skills = collect_skills_from_dataset()
        print(f"  Found {len(ds_skills)} skills in dataset files")
        discovered.update(ds_skills)

        # Scan usage log (real resume uploads)
        usage_skills = collect_skills_from_usage_log()
        print(f"  Found {len(usage_skills)} skills in usage log")
        discovered.update(usage_skills)

        source = "auto_scan"

    # 3. Find genuinely new skills
    print("\n[3/5] Identifying new skills...")
    new_skills = find_new_skills(discovered, existing_skills)

    if not new_skills:
        print("  ✓ No new skills found — ontology is up to date!")
        driver.close()
        return

    print(f"  Found {len(new_skills)} NEW skills not in the graph:")
    for s in sorted(new_skills):
        print(f"    + {s}")

    # 4. Classify with LLM
    print("\n[4/5] Classifying new skills with Gemini...")
    classifications = classify_new_skills(new_skills, existing_skills)
    print(f"  Classified {len(classifications)} skills")

    if dry_run:
        print("\n  [DRY RUN] Would add the following to Neo4j:")
        for c in classifications:
            parent_str = f" → SUBSET_OF → {c.get('parent', '?')}" if c.get('parent') else ""
            related_str = ", ".join(
                f"{r['skill']}({r['similarity']})" for r in c.get('related', [])
            )
            print(f"    {c['skill']}{parent_str}  | Related: {related_str}")
        print("\n  Re-run without --dry-run to apply changes.")
        driver.close()
        return

    # 5. Merge into Neo4j
    print("\n[5/5] Merging into Neo4j graph...")
    stats = merge_into_graph(driver, classifications, existing_skills)

    # Log the expansion
    log_expansion(classifications, stats, source)

    # Print summary
    updated_count = len(get_existing_skills(driver))
    driver.close()

    print("\n" + "=" * 60)
    print("  EXPANSION COMPLETE")
    print("=" * 60)
    print(f"  Nodes added:      {stats['nodes_added']}")
    print(f"  SUBSET_OF edges:  {stats['subset_edges']}")
    print(f"  RELATED_TO edges: {stats['related_edges']}")
    print(f"  Skipped:          {stats['skipped']}")
    print(f"  Total skills now: {updated_count}")
    print(f"  Log saved to:     {EXPANSION_LOG_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-expand the skill ontology")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing to Neo4j")
    parser.add_argument("--from-text", type=str, default=None,
                        help="Extract and classify skills from raw text input")
    args = parser.parse_args()

    expand_ontology(dry_run=args.dry_run, from_text=args.from_text)
