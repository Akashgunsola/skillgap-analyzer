import os
import json
import PyPDF2
from dotenv import load_dotenv
import google.generativeai as genai
import time

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-flash-latest')

def extract_text_from_pdf(pdf_path):
    """Reads text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text.strip()

def batch_extract_skills(docs_dict, doc_type="Job"):
    """
    Takes a dict { "id": "text" }
    Returns a dict { "id": ["skill1", "skill2"] }
    Bundling saves API requests!
    """
    if not docs_dict: return {}
    
    prompt = f"""
You are an expert technical recruiter AI. Extract technical skills, programming languages, and tools for the following {doc_type}s.
Return ONLY a valid JSON object where the keys are exactly the Document IDs provided, and the values are lists of lowercase strings representing the skills.
Example: {{"doc_1": ["python", "docker"], "doc_2": ["react", "node"]}}
Do not include any markdown blocks or explanations, just the raw JSON. Here are the documents:

"""
    for doc_id, text in docs_dict.items():
        # Truncate text just slightly to keep prompt totally safe
        safe_text = text[:3000] 
        prompt += f"--- Document ID: {doc_id} ---\n{safe_text}\n\n"
        
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned)
            time.sleep(4) # Safe offset
            return result
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg:
                wait = 30 * (attempt + 1)
                print(f"    [Rate Limit Hit] Attempt {attempt+1}/{max_retries}, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    [Parsing Error] {e}")
                time.sleep(5)
    return {}

def build_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resumes_dir = os.path.join(base_dir, "data", "raw_resumes")
    jobs_dir = os.path.join(base_dir, "data", "raw_jobs")
    
    dataset = {"resumes": [], "jobs": [], "ground_truth": {}}
    
    # 1. Gather all resume texts
    print("Collecting Resumes...")
    resume_docs = {}
    if os.path.exists(resumes_dir):
        for filename in os.listdir(resumes_dir):
            if filename.lower().endswith('.pdf') or filename.lower().endswith('.txt'):
                file_path = os.path.join(resumes_dir, filename)
                text = ""
                if filename.lower().endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                else:
                    text = extract_text_from_pdf(file_path)
                
                if text:
                    c_id = f"c_{len(resume_docs) + 1}"
                    name = os.path.splitext(filename)[0]
                    resume_docs[c_id] = {"name": name, "text": text}
    
    # 2. Extract Skills in Batches of 15
    chunk_size = 5
    
    if resume_docs:
        print(f"Sending {len(resume_docs)} Resumes to Gemini in batches...")
        # Prepare dict for LLM
        llm_input = {c_id: data["text"] for c_id, data in resume_docs.items()}
        # Since it's only 5 resumes usually, 1 batch is enough
        skills_map = batch_extract_skills(llm_input, doc_type="Resume")
        
        for c_id, data in resume_docs.items():
            dataset["resumes"].append({
                "id": c_id,
                "name": data["name"],
                "skills": skills_map.get(c_id, [])
            })
            print(f"  -> Extracted {len(skills_map.get(c_id, []))} skills for {data['name']}")

    # 3. Gather all job texts
    print("\nCollecting Jobs...")
    job_docs = {}
    if os.path.exists(jobs_dir):
        for filename in os.listdir(jobs_dir):
            if filename.lower().endswith('.txt'):
                with open(os.path.join(jobs_dir, filename), 'r', encoding='utf-8') as f:
                    text = f.read()
                if text.strip():
                    j_id = f"j_{len(job_docs) + 1}"
                    title = os.path.splitext(filename)[0].replace("-", " ").title()
                    job_docs[j_id] = {"title": title, "text": text}

    # 4. Extract Job Skills in Batches to respect the 20/Day limit
    if job_docs:
        print(f"Sending {len(job_docs)} Jobs to Gemini in batches of {chunk_size}...")
        job_items = list(job_docs.items())
        
        skills_map = {}
        for i in range(0, len(job_items), chunk_size):
            chunk = dict(job_items[i:i + chunk_size])
            print(f"  Processing batch {i//chunk_size + 1}...")
            # We pass just the text to LLM mapped by ID
            llm_input = {j_id: data["text"] for j_id, data in chunk.items()}
            chunk_result = batch_extract_skills(llm_input, doc_type="Job")
            skills_map.update(chunk_result)
            time.sleep(8)  # Cooldown between batches to avoid rate limits
            
        for j_id, data in job_docs.items():
            dataset["jobs"].append({
                "id": j_id,
                "title": data["title"],
                "required_skills": skills_map.get(j_id, [])
            })
            print(f"  -> Extracted {len(skills_map.get(j_id, []))} skills for {data['title'][:30]}...")

    output_path = os.path.join(base_dir, "research", "dataset_real.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
        
    print(f"\nSuccessfully built real dataset! (Resumes: {len(dataset['resumes'])}, Jobs: {len(dataset['jobs'])})")

if __name__ == "__main__":
    build_dataset()
