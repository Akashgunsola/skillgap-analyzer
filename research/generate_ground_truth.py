import json
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a standard model with large limits
model = genai.GenerativeModel('gemini-flash-latest')

def generate_batch_ground_truth(input_json_path, output_json_path):
    """
    Optimized approach: Replaces 5,000 requests with just 50 requests using Batch Prompting.
    Sends 1 Resume and all Jobs to the LLM in a single prompt.
    """
    print(f"Loading data from {input_json_path}...")
    with open(input_json_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    resumes = dataset.get("resumes", [])
    jobs = dataset.get("jobs", [])
    
    # Filter out jobs with no extracted skills (failed Gemini calls)
    original_count = len(jobs)
    jobs = [j for j in jobs if j.get("required_skills")]
    dataset["jobs"] = jobs
    if original_count != len(jobs):
        print(f"  Filtered out {original_count - len(jobs)} jobs with 0 skills (rate limit failures)")
    
    if not resumes or not jobs:
        print("ERROR: You must have both Resumes and Jobs in your dataset to generate Ground Truth.")
        return

    # --- RESUMABLE: Load existing ground truth if output file exists ---
    existing_ground_truth = {}
    if os.path.exists(output_json_path):
        try:
            with open(output_json_path, 'r', encoding='utf-8') as ef:
                existing_data = json.load(ef)
                existing_ground_truth = existing_data.get("ground_truth", {})
                print(f"  Loaded existing ground truth with {len(existing_ground_truth)} entries.")
        except Exception:
            print("  Could not load existing output file, starting fresh.")

    synthetic_ground_truth = {candidate["id"]: [] for candidate in resumes}
    # Merge in any existing results
    synthetic_ground_truth.update(existing_ground_truth)

    # Format the jobs catalog once, to be passed in every prompt
    jobs_catalog = "AVAILABLE JOBS:\n"
    for j in jobs:
        j_id = j["id"]
        j_title = j["title"]
        j_skills = ", ".join(j["required_skills"])
        jobs_catalog += f"- ID: {j_id} | Title: {j_title} | Required Skills: {j_skills}\n"

    print(f"Starting Optimized LLM Batch Evaluation for {len(resumes)} Candidate(s) against {len(jobs)} Job(s)...\n")

    for i, candidate in enumerate(resumes):
        c_id = candidate["id"]
        c_name = candidate["name"]
        c_skills = ", ".join(candidate["skills"])
        
        # Skip candidates that already have ground truth results
        if c_id in existing_ground_truth and len(existing_ground_truth[c_id]) > 0:
            print(f"Skipping Candidate [{i+1}/{len(resumes)}]: {c_name} (already has {len(existing_ground_truth[c_id])} matches)")
            continue
        
        print(f"Evaluating Candidate [{i+1}/{len(resumes)}]: {c_name}...")

        prompt = f"""
        You are an expert technical recruiter. I will give you a Candidate Profile and a catalog of Available Jobs.
        
        CANDIDATE:
        Name: {c_name}
        Skills: {c_skills}
        
        {jobs_catalog}
        
        Based ONLY on the skills overlap, evaluate which jobs from this catalog the candidate is highly qualified for.
        Return ONLY a raw JSON array containing the exact IDs of the matching jobs. 
        Example Output format exactly like this: ["j_1", "j_4"]
        Do not include markdown or explanations.
        """

        max_retries = 7
        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                # Parse the JSON response
                cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
                matched_job_ids = json.loads(cleaned_response)
                
                # Ensure it is a list
                if isinstance(matched_job_ids, list):
                    synthetic_ground_truth[c_id] = matched_job_ids
                    print(f"  -> Found {len(matched_job_ids)} matching jobs: {matched_job_ids}")
                else:
                    print(f"  -> Model returned invalid format: {cleaned_response}")
                    
                time.sleep(15) # Longer cooldown between candidates
                break  # Success, move to next candidate
                
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
                    wait = 90 * (attempt + 1)  # 90s base (90, 180, 270, ...)
                    print(f"    [Rate Limit] Attempt {attempt+1}/{max_retries}, waiting {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"Error evaluating {c_name}: {e}")
                    time.sleep(5)
                    break

    dataset["ground_truth"] = synthetic_ground_truth
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
        
    print(f"\nSynthetic ground truth successfully generated and saved to {output_json_path}!")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Switch to pointing towards your newly generated real dataset!
    input_file = os.path.join(base_dir, "dataset_real.json")  
    output_file = os.path.join(base_dir, "dataset_real_with_ground_truth.json") 

    if os.path.exists(input_file):
        generate_batch_ground_truth(input_file, output_file)
    else:
        print(f"Error: Could not find input file at {input_file}. Did you run build_real_dataset.py?")
