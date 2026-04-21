# Playwright Zero-Code Test Generator

Generátor asynchrónnych testov pre Playwright využívajúci umelú inteligenciu (Groq Llama 3.3). 

## Návod na inštaláciu

1. Nainštaluj všetky potrebné závislosti pomocou `pip`:
```bash
pip install -r requirements.txt
```

2. Stiahni a nainštaluj prehliadače pre Playwright (konkrétne Chromium):
```bash
playwright install chromium
```

## Nastavenie
cp .env.example .env
# Otvor .env a vlož svoje kľúče

## Spustenie
Pre vygenerovanie testu spusť skript a ako argument pridaj požadovanú URL (musí začínať na `http://` alebo `https://`):

```bash
python playwright-generator.py <url>
```

**Príklad:**
```bash
python playwright-generator.py https://example.com "Verify login page elements"
```

## Data-Driven Testing
Skript teraz podporuje unikátne názvy súborov pre každý scenár generovania, takže nehrozí prepisovanie už existujúcich testov. Ak zadas rovnaký názov scenára, skript k nemu automaticky pridá aktuálny timestamp (napr. `romotors-ie-contact-form_2026-04-21_1930.spec.ts`).

Navyše je projekt architektonicky pripravený na import a parsovanie externých dát prostredníctvom CSV súborov s vyhradenou zložkou `test_data` a vzorovým súborom `contacts.csv`, čo umožňuje profesionálne vykonávanie Data-Driven testov.
