import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()

def run_guardian(stderr_log: str, dom_dump_path: str = "dom_dump.txt") -> dict:
    # 1. Selector extraction from log
    match = re.search(r"locator\(['\"](.*?)['\"]\)", stderr_log)
    if not match:
        return {"status": "error", "message": "Original selector not found in error log."}
    original_selector = match.group(1)
    
    # 2. Loading DOM dump & QA Standards
    try:
        with open(dom_dump_path, "r", encoding="utf-8") as f:
            dom_content = f.read()
    except FileNotFoundError:
        return {"status": "error", "message": f"File {dom_dump_path} does not exist."}

    # DYNAMIC LOADING OF QA STANDARDS
    try:
        with open("qa_standards.txt", "r", encoding="utf-8") as f:
            qa_rules = f.read()
    except FileNotFoundError:
        qa_rules = "No specific rules provided."

    # 3. AI Call (DeepSeek)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"status": "error", "message": "Missing OPENROUTER_API_KEY in .env file."}

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    prompt = f"""A Playwright test failed because the locator '{original_selector}' is broken or missing.

DOM Dump:
{dom_content}

YOUR TASK:
1. Analyze the original selector ('{original_selector}') to understand its intent.
2. Search the DOM Dump for the correct, updated element that matches this intent.
3. STRICTLY follow these project QA Standards when suggesting the new locator:
{qa_rules}

Return ONLY a clean JSON object with these keys (no markdown text, no ```json at the start):
{{
  "confidence": "HIGH",
  "reasoning": "Explain why the old one failed and why the new one is correct based on QA standards...",
  "locator": "page.locator('...')"
}}

IMPORTANT: Your response must be a valid JSON. Never use unescaped double quotes inside the reasoning field. Use single quotes for HTML attributes."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        ai_text = data['choices'][0]['message']['content'].strip()
        
        # DEBUG: Printing raw response to terminal
        print(f"\n[DEBUG RAW AI RESPONSE]:\n{ai_text}\n")
        
        # AGGRESSIVE MARKDOWN CLEANING & REGEX EXTRACTION
        json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
        if json_match:
            ai_text = json_match.group(0)
        else:
            ai_text = ai_text.strip()
        
        # JSON Parsing with Defensive logic
        try:
            ai_json = json.loads(ai_text)
        except json.JSONDecodeError:
            try:
                clean_text = ai_text.replace('\n', '\\n')
                ai_json = json.loads(clean_text)
            except Exception:
                ai_json = {
                    "confidence": "LOW",
                    "reasoning": "WARNING: AI returned invalid JSON. Using fallback.",
                    "locator": f"page.locator('{original_selector}')"
                }
        
        return {
            "status": "success",
            "original_selector": original_selector,
            "ai_suggestion": ai_json
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to process AI response: {str(e)}\n\nRaw AI text was:\n{ai_text if 'ai_text' in locals() else 'No text'}"
        }