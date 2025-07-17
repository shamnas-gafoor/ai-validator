from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import re
import spacy
import os
from openai import OpenAI
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load spaCy NER
nlp = spacy.load("en_core_web_sm")

# Load piiranha
model_id = "iiiorg/piiranha-v1-detect-personal-information"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForTokenClassification.from_pretrained(model_id)

ner = pipeline("ner", model=model, tokenizer=tokenizer, grouped_entities=True)


# Initialize Presidio engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# --- Regex patterns ---
BLOCK_PATTERNS = [
    r"api[_-]?key\s*[:=]", r"private[_-]?key", r"ssn", r"confidential",
    r"BEGIN (RSA|PRIVATE) KEY", r"\d{13,16}"
]
CODE_PATTERNS = [
    r"\bdef\s+\w+\(", r"\bclass\s+\w+", r"\bfunction\s*\(", r"import\s+\w+", r"console\.log"
]

# --- Redact detected sensitive entities ---
def redact_prompt(prompt: str, results, result_type: str) -> str:
    if result_type == "presidio":
        if not results:
            return prompt
        anonymized = anonymizer.anonymize(text=prompt, analyzer_results=results)
        return anonymized.text
    elif result_type == "regex":
        # results is a list of regex match objects
        redacted_prompt = prompt
        for match in results:
            if match:
                redacted_prompt = redacted_prompt.replace(match.group(), "[REDACTED]")
        return redacted_prompt
    elif result_type == "model":
        # results is the output of the NER model (list of dicts with 'start' and 'end')
        redacted_prompt = list(prompt)
        for entity in results:
            start = entity.get('start')
            end = entity.get('end')
            if start is not None and end is not None:
                for i in range(start, end):
                    redacted_prompt[i] = "*"
        return ''.join(redacted_prompt)
    return prompt

# --- Classification logic ---
def classify_prompt(prompt: str) -> tuple[str, str]:
    # 1. Block if any sensitive pattern matches
    regex_matches = [re.search(pattern, prompt, re.IGNORECASE) for pattern in BLOCK_PATTERNS]
    if any(regex_matches):
        redacted = redact_prompt(prompt, [m for m in regex_matches if m], "regex")
        return "blocked", redacted

    # 2. Warn if looks like source code
    code_matches = [re.search(pattern, prompt, re.IGNORECASE) for pattern in CODE_PATTERNS]
    if any(code_matches):
        redacted = redact_prompt(prompt, [m for m in code_matches if m], "regex")
        return "warning", redacted

    # 3. Presidio for PII
    results = analyzer.analyze(text=prompt, language="en")
    if results:
        redacted = redact_prompt(prompt, results, "presidio")
        return "warning", redacted
    
    # 4. Piiranha for PII
    model_result = ner(prompt)
    if model_result:
        redacted = redact_prompt(prompt, model_result, "model")
        return "blocked", redacted

    return "safe", prompt

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/classify", response_class=HTMLResponse)
async def classify(request: Request, prompt: str = Form(...)):
    print("Starting classification")
    classification, redacted = classify_prompt(prompt)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "prompt": prompt,
        "redacted": redacted,
        "result": classification
    })
