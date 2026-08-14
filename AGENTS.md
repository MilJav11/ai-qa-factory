# AI QA Factory – pravidlá pre agentov

## Účel projektu

Lokálny nástroj na generovanie a human-in-the-loop opravu Playwright E2E testov. Playwright spúšťa aktívne testy a pri zlyhaní zachytáva error trace a DOM. Python/Streamlit poskytuje rozhranie pre Test Generator a Guardian. OpenRouter s modelom DeepSeek analyzuje scenár alebo zlyhanie a navrhne Playwright test či podporovanú opravu selektora. Oprava sa aplikuje na konkrétny test iba po potvrdení používateľa.

## Architektúra

Playwright vykoná test → Guardian uloží chybu a DOM → DOM sa pred AI požiadavkou sanitizuje → AI navrhne opravu → používateľ ju potvrdí → bezpečne sa upraví konkrétny test → test sa môže spustiť znovu.

## Hlavné súbory

- `app.py` – Streamlit UI a potvrdenie zápisu opravy.
- `generator_v1.py` – generovanie Playwright testov cez OpenRouter.
- `guardian_v1.py` – analýza chýb a sanitizovaného DOM, validácia AI odpovede a návrh opravy.
- `guardian_reporter.ts` – uloženie chybového výpisu.
- `tests/fixtures.ts` – zachytenie DOM pri zlyhaní.
- `playwright.config.ts` – konfigurácia aktívnych testov a reportera.
- `qa_standards.txt` – pravidlá pre AI generované testy.
- `tests/` – jediné miesto pre aktívne Playwright testy.
- `_archive_old_prototypes/` – historický kód, ktorý sa nespúšťa.

## Pravidlá práce

- Zachovaj fungujúci human-in-the-loop self-healing workflow; jeho správanie nemeň bez výslovného súhlasu.
- AI môže navrhnúť opravu iba pre podporované výrazy `page.locator(...)`; `getBy*` a komplexné alebo vnorené locator chains nie sú v automatickom repair scope. Používateľ musí návrh explicitne potvrdiť a až potom aplikácia zapíše zmenu do testu.
- Rob iba malú, presne zadanú zmenu a neupravuj súbory mimo zadania.
- Pred väčšou zmenou najprv ukáž plán. Pred úpravou zachovaj necommitnuté zmeny používateľa.
- Nikdy nečítaj ani nevypisuj `.env`, API kľúče, tokeny, certifikáty, credentials ani hodnoty secrets. Pracuj iba s potvrdenými názvami environment premenných v zdrojovom kóde.
- `cleanup_project.py` nespúšťaj bez výslovného povolenia.
- Nerob commit, push, deployment, merge, tag ani mazanie bez výslovného povolenia.
- Aktívne Playwright testy patria iba do `tests/`; `_archive_old_prototypes/` je iba archív.
- Testy vyhľadávaj cez `npx playwright test --list`. Playwright, `npm run guardian`, aplikáciu, sieť, build alebo inštaláciu spúšťaj iba s povolením používateľa.
- Runtime artefakty (DOM dumpy, error logy, `guardian_queue/`, `test-results/`, `playwright-report/`) necommituj.
- Guardian môže zapisovať iba do existujúcich súborov `tests/**/*.spec.ts`; AI locator sa validuje a schválený zápis je atomic.
- Po zmene ukáž diff, uveď riziko a navrhni najmenšie overenie.
- Pri bezpečnostných nálezoch jasne rozlišuj potvrdenú chybu od hypotézy.
