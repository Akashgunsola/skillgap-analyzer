import os
import requests
import json
from dotenv import load_dotenv
import time

load_dotenv()

def fetch_live_jobs(query="developer jobs in chicago", num_pages=1):
    """
    Fetches real-time job postings via JSearch on RapidAPI.
    Requires RAPIDAPI_KEY and RAPIDAPI_HOST in .env.
    """
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    rapidapi_host = os.getenv("RAPIDAPI_HOST")
    
    if not rapidapi_key:
        print("ERROR: Please set your RAPIDAPI_KEY in the .env file.")
        return

    url = f"https://{rapidapi_host}/search"
    
    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": rapidapi_host
    }

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jobs_dir = os.path.join(base_dir, "data", "raw_jobs")
    os.makedirs(jobs_dir, exist_ok=True)
    
    total_fetched = 0
    
    # Process queries using JSearch structure
    querystring = {"query": query, "page": "1", "num_pages": str(num_pages), "date_posted": "all"}
    print(f"Fetching '{query}' jobs from JSearch RapidAPI...")
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        jobs = data.get("data", [])
        for job in jobs:
            # JSearch JSON Schema response fields
            title = job.get("job_title", "Unknown Title")
            company = job.get("employer_name", "Unknown Company")
            description = job.get("job_description", "")
            
            if description:
                # Format a safe filename
                safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                safe_title = safe_title.replace(" ", "_").lower()
                filename = f"live_{safe_title}_{int(time.time())}.txt"
                filepath = os.path.join(jobs_dir, filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"Job Title: {title}\nCompany: {company}\n\nDescription:\n{description}")
                
                total_fetched += 1
                time.sleep(0.01) # ensure valid unique timestamps
        
        print(f"Successfully processed {len(jobs)} jobs.")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        if response is not None:
            print(f"Response: {response.text}")

    print(f"\nDone! Saved {total_fetched} real job descriptions to {jobs_dir}.")
    print("Next Step: Run 'python research/build_real_dataset.py' to extract skills via LLM!")

if __name__ == "__main__":
    import shutil
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    jobs_dir = os.path.join(base_dir, "data", "raw_jobs")
    
    # Auto-clear previous jobs exactly once per run
    if os.path.exists(jobs_dir):
        shutil.rmtree(jobs_dir)
        print("Auto-cleared old jobs from data/raw_jobs/ to ensure a clean dataset.")
    
    # A curated list of distinct IT roles to test your Skill Gap Analyzer comprehensively
    target_roles = [
        "Data Scientist in New York",
        "Frontend React Developer in San Francisco",
        "Backend Python Developer in Austin",
        "Cloud DevOps Engineer in Seattle",
        "Cybersecurity Analyst in Washington DC"
    ]
    
    print("Starting Automated Multi-Role Live Jobs Fetcher...")
    for role in target_roles:
        fetch_live_jobs(query=role, num_pages=1)
        # Sleep for a few seconds between different role searches to be safe with rate limits
        time.sleep(3)
