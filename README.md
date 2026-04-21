# 🤖 AI Playwright Zero-Code Test Generator
An enterprise-grade, AI-driven asynchronous E2E test generator for Playwright, powered by the Groq Llama 3.3 model. This tool autonomously analyzes web structures and writes production-ready TypeScript test suites in seconds.

## 🚀 Installation
Install all required Python dependencies:

```bash
pip install -r requirements.txt
```

Download and install the necessary Playwright browsers (Chromium):

```bash
playwright install chromium
```

## 🔐 Setup & Authentication
Security is our priority. Duplicate the environment template and securely inject your API keys:

```bash
cp .env.example .env
```

Open the `.env` file and insert your respective Groq/Gemini API keys. Never commit this file to version control.

## ⚡ Execution
To trigger the autonomous generator, run the script and provide the target URL (must include `http://` or `https://`) followed by your testing intent in plain English.

```bash
python playwright-generator.py <url> "<scenario_intent>"
```

**Example:**

```bash
python playwright-generator.py https://example.com "Verify login page elements and validate successful authentication flow."
```

## 📊 Data-Driven Testing Architecture
This framework is built for scale. It features dynamic, scenario-based file naming to ensure zero data loss—existing tests are never overwritten. If a scenario with the exact same name is generated, the engine automatically appends a precise timestamp (e.g., `romotors-ie-contact-form_2026-04-21_1930.spec.ts`).

Furthermore, the architecture is fully optimized for Data-Driven Testing (DDT). It includes a dedicated `test_data` directory equipped with a `contacts.csv` template, empowering you to seamlessly map external datasets and execute massive, parameter-driven QA loops right out of the box.
