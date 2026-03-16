import PyPDF2
import sys

def main():
    try:
        reader = PyPDF2.PdfReader('job_companion_and-resume_analyzer_guide.pdf')
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
            
        print("--- BEGIN PDF ---")
        print(text[:3000])
        print("...\n" + text[-3000:])
        print("--- END PDF ---")
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    main()
