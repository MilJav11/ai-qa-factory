import requests
import re
import os

def generate_new_test(api_key: str, url: str, test_description: str) -> str:
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    prompt = f"""Vytvor kompletný e2e Playwright test v TypeScript.
- Použi `import {{ test, expect }} from './fixtures';` (naše fixtures s DOM snapshottingom).
- Začni navigáciou na zadanú URL: {url}
- Pokračuj krok po kroku podľa zadaného popisu: {test_description}
- Dôrazne uprednostňuj sémantické lokátory (napr. `page.locator('button[name="login"]')`) pred IDčkami alebo CSS triedami.
- Pridaj finálnu verifikačnú aserciu (`await expect(...)`) na overenie úspechu.
- Vráť IBA čistý TypeScript kód bez komentárov alebo Markdownu. Žiadne vysvetľovanie."""

    system_prompt = "You are an expert Playwright automation engineer...\n"
    system_prompt += "CRITICAL RULE: Never format URLs as Markdown links inside the code. Always use plain string literals for URLs. WRONG: `await page.goto('[https://example.com](https://example.com)')`. CORRECT: `await page.goto('https://example.com')`.\n"

    if os.path.exists("qa_zrucnosti.txt"):
        with open("qa_zrucnosti.txt", "r", encoding="utf-8") as f:
            qa_rules = f.read()
        system_prompt += f"\nHere are the strict QA guidelines you MUST follow:\n{qa_rules}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        ai_text = data['choices'][0]['message']['content'].strip()
        
        # Bezpečnostné ošetrenie prípadného Markdown formátovania, ak LLM neposlúchne
        match = re.search(r'```(?:typescript|ts)?\s*(.*?)\s*```', ai_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return ai_text.strip()
        
    except Exception as e:
        return f"// Error: Failed to generate test.\n// Details: {str(e)}"
