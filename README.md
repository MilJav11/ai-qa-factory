# 🛡️ Playwright AI QA Factory & Guardian
An integrated AI-powered framework for end-to-end test automation. This project combines two core capabilities:

- **AI Test Generator**: Generates clean, robust Playwright tests from natural language descriptions, adhering to custom QA standards.
- **AI Guardian (Auto-Healer)**: Automatically detects, analyzes, and fixes broken locators in Playwright tests using LLM analysis.

## 🚀 Quick Start
Launch the integrated dashboard to access both the Generator and the Guardian:

```bash
python -m streamlit run app.py
```

## 🛠️ Key Features
- **AI Test Generator**: Creates TypeScript E2E tests following strict rules defined in `qa_standards.txt`.
- **Self-Healing Mechanism**: Captures DOM snapshots and error logs upon failure, then uses LLM analysis to suggest and patch the correct locators.
- **Unified UI**: A Streamlit dashboard for managing test generation and applying one-click fixes.
- **Custom Reporter**: Integrated logging system that saves `error_log.txt` and `dom_dump.txt` for AI diagnosis.

## 📖 Installation
- Install dependencies: `npm install && npx playwright install`
- Install Python requirements: `pip install -r requirements.txt`
- Configure API: Create a `.env` file and add your `OPENROUTER_API_KEY`.

## 🤖 Command Center (For AI Maintenance)
When you need to modify the framework, use these maintenance instructions:

- **To update test standards**: 'Modify `generator_v1.py` to strictly enforce the rules defined in `qa_standards.txt` and ensure URLs are always formatted as plain strings.'
- **To update UI logic**: 'Modify `app.py` to handle automated file storage in the `/tests` directory and display clear success feedback.'

## 🏗️ Project Structure
- `app.py`: Central Streamlit dashboard.
- `generator_v1.py`: Logic for test generation.
- `guardian_v1.py`: Analysis and patching logic.
- `tests/`: Directory for generated and healed test files.
- `qa_standards.txt`: Core knowledge base defining custom QA rules.
