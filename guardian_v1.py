import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()

def run_guardian(stderr_log: str) -> dict:
    # 1. Selector extraction from log
    match = re.search(r"locator\(['\"](.*?)['\"]\)", stderr_log)
    if not match:
        return {"status": "error", "message": "Original selector not found in error log."}
    original_selector = match.group(1)
    
    # 2. Loading DOM dump
    try:
        with open("dom_dump.txt", "r", encoding="utf-8") as f:
            dom_content = f.read()
    except FileNotFoundError:
        return {"status": "error", "message": "File dom_dump.txt does not exist. Nothing to read from."}

    # 3. AI Call (DeepSeek)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"status": "error", "message": "Missing OPENROUTER_API_KEY in .env file."}

    url = "https://openrouter.ai/api/v1/chat/completions"
    prompt = f"""Test failed with 'Strict Mode Violation'.
Selector: '{original_selector}'

DOM Dump:
{dom_content}

Return ONLY a clean JSON object with these keys (no markdown text, no ```json at the start):
{{
  "confidence": "HIGH",
  "reasoning": "Reasoning in English...",
  "locator": "page.locator('...')"
}}"""

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
        
        # DEBUG: Printing raw response to terminal to see the truth
        print(f"\n[DEBUG RAW AI RESPONSE]:\n{ai_text}\n")
        
        # AGGRESSIVE MARKDOWN CLEANING
        if ai_text.startswith("```json"):
            ai_text = ai_text[7:]
        if ai_text.startswith("```"):
            ai_text = ai_text[3:]
        if ai_text.endswith("```"):
            ai_text = ai_text[:-3]
        ai_text = ai_text.strip()
        
        # JSON Parsing
        ai_json = json.loads(ai_text)
        
        return {
            "status": "success",
            "original_selector": original_selector,
            "ai_suggestion": ai_json
        }
        
    except Exception as e:
        # NO MORE HIDING! If it fails, show it in UI.
        return {
            "status": "error",
            "message": f"Failed to process AI response: {str(e)}\n\nRaw AI text was:\n{ai_text if 'ai_text' in locals() else 'No text'}"
        }