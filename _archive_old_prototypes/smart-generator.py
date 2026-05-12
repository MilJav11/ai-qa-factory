import sys
import os
import time
import subprocess
from datetime import datetime
from functools import wraps
from groq import Groq
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf-8')

def meraj_cas(func):
    """Univerzálny dekorátor na meranie času akejkoľvek funkcie."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        t_start = time.time()
        vysledok = func(*args, **kwargs)
        t_end = time.time()
        print(f"⏱️  [METRIKA] '{func.__name__}' trvalo: {t_end - t_start:.1f}s")
        return vysledok
    return wrapper

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def load_skills():
    """Načíta externý mozog (QA Zručnosti) zo súboru."""
    try:
        with open("qa_zrucnosti.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Žiadne dodatočné QA pravidlá neboli nájdené."

@meraj_cas
def scan_dom(url):
    print(f"🕵️ Prieskumník skenuje: {url} ...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            
            # --- NOVINKA: Preskrolujeme stránku až dole a hore, aby sa všetko načítalo ---
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000) # Počkáme na animácie/lazy load
            page.evaluate("window.scrollTo(0, 0)")
            # -------------------------------------------------------------------------

            print("🍪 Hľadám a ničím Cookie lišty...")
            cookie_buttons = ['text="Rozumiem"', 'text="Súhlasím"', 'text="Prijať všetko"', 'text="Accept all"', 'a.js-cookies-info-accept']
            for btn in cookie_buttons:
                try:
                    page.locator(btn).first.click(timeout=2000)
                    print(f"✅ Cookie lišta zničená pomocou: {btn}")
                    page.wait_for_timeout(1000)
                    break
                except:
                    pass

            # --- CHIRURGICKÝ FILTER DOM MAPY ---
            elementy = page.evaluate("""() => {
                const noiseSelectors = 'header, footer, nav, aside, .menu, .sidebar, #header, #colophon';
                const els = Array.from(document.querySelectorAll('input, button, select, textarea, [role="button"], a'));
                
                return els.map(el => {
                    const isNoise = el.closest(noiseSelectors) !== null;
                    
                    // Bezpecnostna poistka: Ignorujeme len ODKAZY (<a>) v hlavicke/paticke.
                    // Formularove polia a tlacidla zachovavame vzdy.
                    if (el.tagName === 'A' && isNoise) return null;

                    return {
                        tag: el.tagName.toLowerCase(),
                        type: el.getAttribute('type') || '',
                        id: el.id || '',
                        name: el.getAttribute('name') || '',
                        placeholder: el.getAttribute('placeholder') || '',
                        text: el.innerText ? el.innerText.trim().substring(0, 20) : ''
                    };
                }).filter(e => e !== null && e.type !== 'hidden' && e.type !== 'submit');
            }""")
            # ------------------------------------
            browser.close()
            return "\n".join([f"<{e['tag']} id='{e['id']}' name='{e['name']}' placeholder='{e['placeholder']}'> {e['text']}" for e in elementy])
    except Exception as e:
        return f"Mapa DOM nie je dostupná: {e}"

# --- ZOZNAM MODELOV PRE KASKÁDU ---
# 1. llama-3.3-70b-versatile (Senior - inteligentný, ale má nízke limity)
# 2. llama-3.1-8b-instant (Junior - bleskový, vysoké limity, skvelý na opravy)
AI_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

@meraj_cas
def ask_ai(prompt):
    for model_name in AI_MODELS:
        try:
            # Skúsime zavolať aktuálny model v poradí
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
                temperature=0.1
            )
            print(f"🤖 [AI ENGINE] Odpoveď vygeneroval model: {model_name}")
            return response.choices[0].message.content.replace("```typescript", "").replace("```", "").strip()
        
        except Exception as e:
            # Ak dostaneme Rate Limit (chyba 429) alebo hocičo iné
            if "429" in str(e):
                print(f"⚠️ Model {model_name} dosiahol limit (Rate Limit). Kaskáda prepína na záložný model...")
                continue # Skočí na ďalší model v zozname AI_MODELS
            else:
                print(f"❌ Neočakávaná chyba pri modeli {model_name}: {e}")
                continue
                
    # Ak prejdeme všetky modely a nič nefunguje
    print("💀 KRITICKÁ CHYBA: Všetky AI modely v kaskáde sú nedostupné alebo vyčerpané.")
    sys.exit(1)

def generate_initial_test(url, scenario, dom_map, skills):
    print("🧠 Generujem prvotný kód (s využitím QA Zručností)...")
    prompt = f"""
    Write a complete Playwright test in TypeScript for {url}.
    Scenario: {scenario}
    
    --- REAL DOM MAP ---
    {dom_map}
    
    --- SENIOR QA KNOWLEDGE BASE (CRITICAL RULES) ---
    {skills}
    
    Output ONLY raw TypeScript code.
    """
    return ask_ai(prompt)

@meraj_cas
def run_test(filename):
    print(f"🚀 Spúšťam test: {filename} ...")
    result = subprocess.run(f"npx playwright test {filename}", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    stdout = result.stdout if result.stdout else ""
    stderr = result.stderr if result.stderr else ""
    return result.returncode == 0, stdout + stderr

def heal_code(url, scenario, old_code, error_log, dom_map, qa_skills):
    print("🩹 Test zlyhal. Spúšťam proces samoopravenia (Healing)...")
    prompt = f"""OPRAV PLAYWRIGHT TEST. ZLYHAL.
URL: {url}
ZADANIE: {scenario}

ZRUCNOSTI (DODRZUJ):
{qa_skills}

DOSTUPNY DOM (FILTROVANY):
{dom_map}

KOD, KTORY ZLYHAL:
```typescript
{old_code}
```

CHYBA (LOG):
{error_log}

NAVOD:
- Analyzuj CHYBU. Ak je to timeout na lokatore, najdi iny v DOSTUPNY DOM.
- Ak je chyba "intercepted", pouzi force: true.
- Vrat LEN opraveny typescript kod, ziadne vysvetlovanie."""
    return ask_ai(prompt)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Použitie: python smart-generator.py <url> <scenario>")
        sys.exit(1)

    u, s = sys.argv[1], sys.argv[2]
    d_map = scan_dom(u)
    qa_skills = load_skills() # Načítanie nášho externého mozgu
    
    code = generate_initial_test(u, s, d_map, qa_skills)
    
    filename = f"auto_test_{datetime.now().strftime('%H%M%S')}.spec.ts"
    with open(filename, "w", encoding="utf-8") as f: f.write(code)

    for attempt in range(3):
        success, logs = run_test(filename)
        if success:
            print(f"✅ TEST PREŠIEL NA {attempt+1}. POKUS!")
            break
        else:
            if attempt < 2:
                code = heal_code(u, s, code, logs, d_map, qa_skills)
                with open(filename, "w", encoding="utf-8") as f: f.write(code)
            else:
                print("❌ Test nebolo možné opraviť ani na 3 pokusy.")
                print("Posledný Error Log:", logs)
