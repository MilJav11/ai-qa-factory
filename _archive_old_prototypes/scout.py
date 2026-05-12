from playwright.sync_api import sync_playwright

def preskumaj_stranku(url):
    print(f"🕵️ Prieskumník štartuje: {url}\n")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        # JavaScript, ktorý z webu vytiahne len to dôležité "mäso"
        elementy = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('input, button, a[href*="compose"]'));
            return els.map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.getAttribute('type') || '',
                id: el.id || '',
                placeholder: el.getAttribute('placeholder') || '',
                text: el.innerText ? el.innerText.trim().substring(0, 30) : ''
            })).filter(e => e.type !== 'hidden'); // Zahodíme neviditeľný balast
        }""")
        
        print("--- NÁJDENÉ ELEMENTY PRE AI ---")
        for el in elementy:
            print(f"Tag: <{el['tag']}> | Type: '{el['type']}' | ID: '{el['id']}' | Placeholder: '{el['placeholder']}' | Text: '{el['text']}'")
            
        browser.close()
        print("\n✅ Prieskum ukončený.")

if __name__ == "__main__":
    # Ideme otestovať tú našu nočnú moru
    preskumaj_stranku("https://email.seznam.cz")
