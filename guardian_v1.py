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
    
    # 2. Loading DOM dump
    try:
        with open(dom_dump_path, "r", encoding="utf-8") as f:
            dom_content = f.read()
    except FileNotFoundError:
        return {"status": "error", "message": f"File {dom_dump_path} does not exist. Nothing to read from."}

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
}}

IMPORTANT: Your response must be a valid JSON. Never use unescaped double quotes inside the reasoning field. Use single quotes for HTML attributes or escape double quotes with a backslash."""

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
            # Basic cleaning logic: try removing problematic newlines and fix basic quotes
            try:
                # Try a mild clean up first
                clean_text = ai_text.replace('\n', '\\n')
                ai_json = json.loads(clean_text)
            except Exception:
                # If it's totally unreadable, fallback instead of crashing
                ai_json = {
                    "confidence": "LOW",
                    "reasoning": "WARNING: AI returned invalid JSON. Using fallback.",
                    "locator": original_selector
                }
        
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