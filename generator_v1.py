import requests
import re
import os

def generate_new_test(api_key: str, url: str, test_description: str) -> str:
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    prompt = f"""Create a complete e2e Playwright test in TypeScript.
- Use `import {{ test, expect }} from './fixtures';` (our fixtures with DOM snapshotting).
- Start by navigating to the specified URL: {url}
- Continue step-by-step according to the provided description: {test_description}
- Strongly prefer semantic locators (e.g., `page.locator('button[name="login"]')`) over IDs or CSS classes.
- Add a final verification assertion (`await expect(...)`) to verify success.
- Return ONLY clean TypeScript code without comments or Markdown. No explanations."""

    system_prompt = "You are an expert Playwright automation engineer...\n"
    system_prompt += "CRITICAL RULE: Never format URLs as Markdown links inside the code. Always use plain string literals for URLs. WRONG: `await page.goto('[https://example.com](https://example.com)')`. CORRECT: `await page.goto('https://example.com')`.\n"

    if os.path.exists("qa_standards.txt"):
        with open("qa_standards.txt", "r", encoding="utf-8") as f:
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
        
        # Safety handling for potential Markdown formatting, in case LLM ignores instructions
        match = re.search(r'```(?:typescript|ts)?\s*(.*?)\s*```', ai_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return ai_text.strip()
        
    except Exception as e:
        return f"// Error: Failed to generate test.\n// Details: {str(e)}"
