import asyncio
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import re
import bs4
from playwright.async_api import async_playwright
import groq
from google import genai
from dotenv import load_dotenv

load_dotenv()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python playwright-generator.py <url>")
        sys.exit(1)
        
    url = sys.argv[1]
    if not url.startswith("http://") and not url.startswith("https://"):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)
        
    scenario = sys.argv[2] if len(sys.argv) > 2 else "Verify that the main elements on the page are visible and accessible."

    start_time = time.time()
    
    # Fáza 1: Playwright
    title = ""
    aria_tree = ""
    print(f"Opening URL: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(1.5)
            
            # Fáza 2: Extrakcia
            title = await page.title()
            try:
                aria_tree = await page.locator("body").aria_snapshot()
                if not aria_tree:
                    raise ValueError("Empty aria snapshot")
            except Exception as e:
                print("Aria snapshot failed, falling back to BeautifulSoup...")
                html_content = await page.content()
                soup = bs4.BeautifulSoup(html_content, 'html.parser')
                for tag in soup(["script", "style", "svg", "noscript"]):
                    tag.decompose()
                aria_tree = soup.get_text(separator=' ', strip=True)
                
            if len(aria_tree) > 32000:
                print("Content too long, truncating...")
                aria_tree = aria_tree[:32000] + "\n[TRUNCATED]"
                
            await browser.close()
    except Exception as e:
        print(f"Error during Playwright execution: {e}")
        sys.exit(1)

    # Fáza 3: Groq
    print("Generating test code using Groq...")
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            print("Error: GROQ_API_KEY is not set in .env")
            sys.exit(1)
            
        client = groq.AsyncGroq(api_key=groq_api_key)
        
        golden_sample_path = os.path.join("golden_samples", "standard_pom.ts.sample")
        with open(golden_sample_path, "r", encoding="utf-8") as f:
            golden_sample_content = f.read()
            
        system_prompt = """Si Senior QA Automation Engineer. Tvojou úlohou je vygenerovať Playwright test v TypeScripte.
ZAKAZUJEM používať XPath a CSS selektory, používaj výhradne web-first lokátory (getByRole, getByPlaceholder atď.) a pridávaj na koniec .first().
MUSÍŠ presne skopírovať architektonický štýl (dizajn POM, dedičnosť, test.describe, test.beforeEach), ktorý je ukázaný v Zlatej Vzorke. Nevymýšľaj vlastnú štruktúru. 10. Pri hľadaní textových polí (textarea) sa nespoliehaj len na slovo 'message'. Ak v ARIA strome vidíš dlhšiu vetu v placeholderi (napr. 'How can we help you?'), použi kľúčové slová z tej vety v regulárnom výraze pre getByPlaceholder."""
        
        user_prompt = f"""--- ZLATÁ VZORKA ---
{golden_sample_content}
--------------------

URL: {url}
Title: {title}

Príslušný ARIA content:
{aria_tree}

SCENÁR NA NAPROGRAMOVANIE: {scenario}. Vytvor POM a test, ktorý vykoná tento scenár krok za krokom."""
        
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2048
        )
        
        generated_response = completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error during Groq execution: {e}")
        sys.exit(1)

    # Fáza 4: Post-processing
    print("Processing generated code...")
    try:
        match = re.search(r'```typescript\n(.*?)```', generated_response, re.DOTALL)
        if match:
            generated_code = match.group(1).strip()
        else:
            match = re.search(r'```ts\n(.*?)```', generated_response, re.DOTALL)
            if match:
                generated_code = match.group(1).strip()
            else:
                 generated_code = generated_response.strip()
            
        # Generate filename from URL and scenario
        import datetime
        
        domain = re.sub(r'^https?://(www\.)?', '', url)
        domain = re.sub(r'[^a-zA-Z0-9]', '-', domain)
        domain = re.sub(r'-+', '-', domain).strip('-')
        if not domain:
            domain = "unknown"
            
        if scenario == "Verify that the main elements on the page are visible and accessible.":
            scenario_slug = "default"
        else:
            scenario_slug = re.sub(r'[^a-zA-Z0-9]', '-', scenario.lower())
            scenario_slug = re.sub(r'-+', '-', scenario_slug).strip('-')
            if len(scenario_slug) > 30:
                scenario_slug = scenario_slug[:30].strip('-')
        
        filename = f"{domain}-{scenario_slug}.spec.ts"
        
        if os.path.exists(filename):
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
            filename = f"{domain}-{scenario_slug}_{timestamp}.spec.ts"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(generated_code)
            
        lines_count = len(generated_code.splitlines())
        duration = time.time() - start_time
        print(f"File '{filename}' generated successfully!")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Lines of code: {lines_count}")
        
    except Exception as e:
        print(f"Error during post-processing: {e}")
        sys.exit(1)
        
    # Fáza 5: Gemini Validácia
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key and gemini_api_key != "tvoj_gemini_kluc_sem":
        print("Validating with Gemini...")
        try:
            client = genai.Client(api_key=gemini_api_key)
            
            gemini_prompt = f"Skontroluj tento Playwright TS test. Oznám len chyby (XPath, chýbajúce assertions, zlé importy). Ak je OK, odpovedz: PASS. Kód:\n\n{generated_code}"
            
            response = client.models.generate_content(model="gemini-3-flash-preview", contents=gemini_prompt)
            print("🔍 Gemini review:", response.text.strip())
            
        except Exception as e:
             print(f"Error during Gemini validation: {e}")
    else:
        print("Skipping Gemini validation (GEMINI_API_KEY not set or is default)")

if __name__ == "__main__":
    asyncio.run(main())
