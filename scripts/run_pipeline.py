import os
import json
import requests
from docx import Document

# ==================================================
# CONFIG
# ==================================================
# ==================================================
# CONFIG (FIXED PATH HANDLING)
# ==================================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PROMPT_DIR = os.path.join(BASE_DIR, "prompts")
DATA_DIR = os.path.join(BASE_DIR, "data", "input")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:latest"

MAX_CONTEXT = 4000


# ==================================================
# DOCX READER
# ==================================================
def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


# ==================================================
# LOAD DOCUMENTS (TXT + DOCX)
# ==================================================
def load_docs():
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"Missing folder: {DATA_DIR}")

    docs = []

    for file in sorted(os.listdir(DATA_DIR)):
        path = os.path.join(DATA_DIR, file)

        if file.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())

        elif file.endswith(".docx"):
            docs.append(read_docx(path))

    combined = "\n\n".join(docs).strip()

    if not combined:
        raise ValueError("No readable documents found")

    return combined[:MAX_CONTEXT]


# ==================================================
# LOAD PROMPT
# ==================================================
def load_prompt(name):
    path = os.path.join(PROMPT_DIR, f"{name}.txt")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing prompt: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


# ==================================================
# OLLAMA CALL (SAFE + CONTROLLED)
# ==================================================
def call_llm(prompt, input_text):
    payload = {
        "model": MODEL,
        "prompt": f"""
You are a strict information extraction system.

RULES:
- Do NOT hallucinate
- Use ONLY provided text
- If unsure, output "UNKNOWN"
- Keep output structured and minimal

TASK:
{prompt}

INPUT:
{input_text}
""",
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=120)
        res.raise_for_status()
        return res.json()["response"]
    except Exception as e:
        return f"ERROR: {str(e)}"


# ==================================================
# PIPELINE
# ==================================================
def run_pipeline(docs):

    print("\n[1] BRIEFING...")
    brief = call_llm(load_prompt("briefing"), docs)

    print("\n[2] EXTRACTION...")
    extracted = call_llm(load_prompt("extract"), brief)

    print("\n[3] FILTERING...")
    filtered = call_llm(load_prompt("filter"), extracted)

    print("\n[4] STRUCTURING...")
    structured = call_llm(load_prompt("structure"), filtered)

    print("\n[5] VALIDATION...")
    validated = call_llm(load_prompt("validate"), structured)

    # FORCE CLEAN JSON OUTPUT
    try:
        parsed = json.loads(validated)
    except:
        parsed = {
            "error": "Invalid JSON output from model",
            "raw_output": validated
        }

    return parsed


# ==================================================
# MAIN
# ==================================================
if __name__ == "__main__":

    print("Loading documents...")

    docs = load_docs()

    print("Running pipeline...")

    output = run_pipeline(docs)

    print("\n================ FINAL JSON OUTPUT ================\n")

    print(json.dumps(output, indent=2, ensure_ascii=False))