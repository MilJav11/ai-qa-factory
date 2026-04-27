# 🛡️ Playwright AI Guardian

An AI-powered self-healing test automation framework that automatically detects, analyzes, and fixes broken Playwright locators using DeepSeek LLM.

## 🚀 Quick Start (Automated)
Instead of running commands separately, use the integrated guardian script:
```bash
npm run guardian
```

## 🚀 Key Features

- **Custom Reporter**: Automatically captures detailed error logs and stacks upon test failure.
- **Automatic DOM Snapshotting**: Saves the exact state of the DOM at the moment of failure for AI analysis.
- **AI Analysis via Streamlit UI**: Provides a user-friendly dashboard to analyze failures and suggests optimized locators.
- **One-click Auto-patching**: Automatically updates your test files with the AI-suggested locators.

## 🛠️ Installation

### 1. Prerequisites
- Node.js (v16 or higher)
- Python (3.8 or higher)

### 2. Install Dependencies
Install Playwright and Node dependencies:
```bash
npm install
npx playwright install
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_key_here
```

## 📖 Usage

### 1. Run Your Tests
Execute your Playwright tests using the Guardian Reporter:
```bash
npx playwright test --reporter=./guardian_reporter.ts
```
If a test fails, the reporter will generate `error_log.txt` and the fixture will save `dom_dump.txt`.

### 2. Launch the AI Dashboard
Start the Streamlit dashboard to analyze and fix the errors:
```bash
streamlit run app.py
```

### 3. Apply Fixes
1. Open the dashboard in your browser (usually `http://localhost:8501`).
2. Review the AI analysis and the suggested locator.
3. Verify the target file path.
4. Click **"Overwrite code in file"** to automatically patch your test.

## 🏗️ Project Structure

- `app.py`: Streamlit dashboard for AI analysis and patching.
- `guardian_v1.py`: AI logic and integration with DeepSeek via OpenRouter.
- `guardian_reporter.ts`: Custom Playwright reporter for error capturing.
- `tests/fixtures.ts`: Playwright fixtures for DOM snapshotting.
- `error_parser.py`: Utility for parsing Playwright error logs.
