# 🛡️ Playwright AI QA Factory & Guardian
**An Agentic E2E Test Framework with Autonomous Self-Healing Capabilities.**

This project is a 3-Layer Orchestration System designed to eliminate test flakiness and automate the maintenance of complex microservices UIs.

## 🏗️ The Architecture
- **Execution Layer (Playwright):** Standard E2E execution generating DOM Dumps + Error Traces.
- **Control Plane (Python/Streamlit):** Local orchestrator managing the failure queue and defensive guardrails.
- **Cognitive Engine (DeepSeek V4 via OpenRouter):** Deterministic AI model (Temp 0.0) performing Root Cause Analysis.

## 🚀 The Auto-Healer Workflow
- **Detection:** Custom reporter catches failures.
- **Context Capture:** Generates a full DOM Dump at the second of failure.
- **Heuristic Analysis:** AI analyzes intent vs. current DOM state.
- **Autonomous Patching:** System overwrites broken code using defensive regex patterns.

## 🛠️ Features
- **✨ Test Generator:** Creates TS tests following strict 'qa_standards.txt'.
- **🚑 Enterprise Queue:** Batch-processes failures from CI/CD.
- **🛡️ Defensive AI:** Robust JSON parsing with fallback chains.

## 🧠 Philosophy: Determinism over Creativity
The framework uses 'temperature: 0.0'. We don't want "creative" AI; we want a deterministic logic engine that treats 'qa_standards.txt' as immutable law.
