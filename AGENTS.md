# AI QA Factory – pravidlá pre agentov

## Účel projektu

Lokálny agentický nástroj na generovanie a self-healing Playwright E2E testov. Playwright spúšťa testy a pri zlyhaní zachytáva error trace a DOM. Python/Streamlit poskytuje používateľské rozhranie pre Test Generator a Guardian. OpenRouter s modelom DeepSeek analyzuje scenár alebo zlyhanie a navrhuje Playwright test či opravu selektora. Oprava sa aplikuje na konkrétny test až po potvrdení používateľa.

## Architektúra

Playwright vykoná test → Guardian uloží chybu a DOM → AI navrhne opravu → používateľ ju potvrdí → upraví sa konkrétny test → test znovu prejde.

## Hlavné súbory

- `app.py` – Streamlit UI a potvrdenie zápisu opravy.
- `generator_v1.py` – generovanie Playwright testov cez OpenRouter.
- `guardian_v1.py` – analýza chýb, DOM a návrh opravy.
- `guardian_reporter.ts` – uloženie chybového výpisu.
- `tests/fixtures.ts` – zachytenie DOM pri zlyhaní.
- `playwright.config.ts` – konfigurácia aktívnych testov a reportera.
- `qa_standards.txt` – pravidlá pre AI generované testy.
- `tests/` – aktívne testy.
- `_archive_old_prototypes/` – historický kód, ktorý sa nemá spúšťať.

## Pravidlá práce

- Zachovaj existujúci self-healing workflow; jeho správanie nemeň bez výslovného súhlasu.
- Rob iba malú, presne zadanú zmenu a neupravuj súbory mimo zadania.
- Pred väčšou zmenou najprv ukáž plán. Pred úpravou zachovaj necommitnuté zmeny používateľa.
- Nikdy nečítaj ani nevypisuj `.env`, API kľúče, tokeny, certifikáty ani credentials.
- `cleanup_project.py` nespúšťaj bez výslovného povolenia.
- Nerob commit, push, deployment ani mazanie bez výslovného povolenia.
- Testy vyhľadávaj cez `npx playwright test --list`. Hlavný workflow over cez `npm run guardian` iba s povolením používateľa.
- Aktívne Playwright testy patria do `tests/`; `_archive_old_prototypes/` je iba archív.
- Runtime artefakty (DOM dumpy, error logy, `guardian_queue/`, `test-results/`, `playwright-report/`) necommituj.
- Po zmene ukáž diff, uveď riziko a navrhni najmenšie overenie.
- Pri bezpečnostných nálezoch jasne rozlišuj potvrdenú chybu od hypotézy.
