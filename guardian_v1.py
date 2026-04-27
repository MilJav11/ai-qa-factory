import os
import json
import requests
import re
from dotenv import load_dotenv

load_dotenv()

def run_guardian(stderr_log: str) -> dict:
    # 1. Extrakcia selektora z logu
    match = re.search(r"locator\(['\"](.*?)['\"]\)", stderr_log)
    if not match:
        return {"status": "error", "message": "Nenašiel som pôvodný selektor v chybovom logu."}
    original_selector = match.group(1)
    
    # 2. Načítanie DOM dumpu
    try:
        with open("dom_dump.txt", "r", encoding="utf-8") as f:
            dom_content = f.read()
    except FileNotFoundError:
        return {"status": "error", "message": "Súbor dom_dump.txt neexistuje. Nemám z čoho čítať."}

    # 3. Volanie AI (DeepSeek)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"status": "error", "message": "Chýba OPENROUTER_API_KEY v .env súbore."}

    url = "https://openrouter.ai/api/v1/chat/completions"
    prompt = f"""Test padol na 'Strict Mode Violation'.
Selektor: '{original_selector}'

DOM Dump:
{dom_content}

Vráť IBA čistý JSON objekt s týmito kľúčmi (žiadny markdown text, žiadne ```json na začiatku):
{{
  "confidence": "HIGH",
  "reasoning": "Zdôvodnenie v slovenčine...",
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
        
        # DEBUG: Vypíšeme surovú odpoveď do terminálu, aby sme videli pravdu
        print(f"\n[DEBUG RAW AI RESPONSE]:\n{ai_text}\n")
        
        # AGRESÍVNE ČISTENIE MARKDOWNU
        if ai_text.startswith("```json"):
            ai_text = ai_text[7:]
        if ai_text.startswith("```"):
            ai_text = ai_text[3:]
        if ai_text.endswith("```"):
            ai_text = ai_text[:-3]
        ai_text = ai_text.strip()
        
        # Parsovanie JSONu
        ai_json = json.loads(ai_text)
        
        return {
            "status": "success",
            "original_selector": original_selector,
            "ai_suggestion": ai_json
        }
        
    except Exception as e:
        # UŽ ŽIADNE SKRÝVANIE! Ak to spadne, ukážeme to v UI.
        return {
            "status": "error",
            "message": f"Zlyhalo spracovanie odpovede od AI: {str(e)}\n\nSurový text od AI bol:\n{ai_text if 'ai_text' in locals() else 'Žiadny text'}"
        }