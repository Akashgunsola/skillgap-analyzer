import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

test_models = ['gemini-flash-latest', 'gemini-2.5-flash-lite', 'gemini-1.5-flash-latest', 'gemma-3-27b-it', 'gemini-2.5-pro', 'gemini-2.5-flash']

for m in test_models:
    try:
        model = genai.GenerativeModel(m)
        resp = model.generate_content('hello')
        print(f'SUCCESS: {m}')
        break
    except Exception as e:
        print(f'FAILED {m}')
