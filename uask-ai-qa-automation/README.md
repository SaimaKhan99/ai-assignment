# U-Ask AI QA Automation Framework

## Overview

This repository contains a production-style end-to-end QA automation framework for the UAE Government generative AI assistant, U-Ask.

Target application:

- `https://beta-ask.u.ae/en/uask`

The framework validates:

- Chatbot UI behavior
- AI response rendering quality
- English and Arabic response behavior
- Prompt injection resistance
- XSS and suspicious input handling
- Lightweight hallucination heuristics
- Reliability and semantic consistency
- Response latency
- Basic accessibility behavior
- Logging, screenshots, and HTML reporting

## Why AI/LLM Testing Differs From Traditional Automation

Traditional UI and API automation usually validates deterministic outputs. LLM systems are different:

- Responses vary in wording even when behavior is correct.
- Exact string matching is usually the wrong assertion strategy.
- A response can be syntactically valid but semantically irrelevant.
- Security validation must include adversarial prompts, not just malformed inputs.
- Reliability is measured through relevance, structure, and consistency, not exact duplication.

This framework uses layered validation to reflect those realities:

- Basic non-empty checks
- Structural sanity checks
- Keyword relevance checks
- Semantic similarity checks with `all-MiniLM-L6-v2`
- Heuristic hallucination and adversarial-behavior checks

## Framework Architecture

The framework is organized around:

- Page Object Model for resilient UI interaction
- Validator classes for AI-specific assertions
- Utility modules for logging, screenshots, performance, and language detection
- JSON-driven test data
- Pytest fixtures for browser/session reuse

Key design choices:

- Live-site aware selectors use a fallback strategy
- Assertions are tolerant to wording variation
- Failure artifacts are automatically captured
- Config values are centralized and easy to extend

## Folder Structure

```text
uask-ai-qa-automation/
├── tests/
│   ├── conftest.py
│   ├── test_ui_behavior.py
│   ├── test_ai_responses.py
│   ├── test_multilingual.py
│   ├── test_security.py
│   ├── test_performance.py
│   ├── test_reliability.py
│   └── test_accessibility.py
├── pages/
│   └── chatbot_page.py
├── validators/
│   ├── response_validator.py
│   ├── semantic_validator.py
│   ├── hallucination_detector.py
│   └── security_validator.py
├── utils/
│   ├── logger.py
│   ├── language_utils.py
│   ├── performance_utils.py
│   ├── screenshot_utils.py
│   └── config.py
├── testdata/
│   └── test-data.json
├── screenshots/
├── logs/
├── reports/
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- Python `3.11+`
- Internet access to the live U-Ask beta site
- Ability to download Playwright browser binaries

## Setup Instructions

Clone or place this project locally, then work from the repository root:

```bash
cd uask-ai-qa-automation
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Install Playwright Browsers

```bash
playwright install
```

## How To Run All Tests

```bash
pytest tests --html=reports/report.html --self-contained-html
```

## How To Run Individual Test Files

```bash
pytest tests/test_ui_behavior.py
pytest tests/test_ai_responses.py
pytest tests/test_multilingual.py
pytest tests/test_security.py
pytest tests/test_performance.py
pytest tests/test_reliability.py
pytest tests/test_accessibility.py
```

## How To Generate HTML Report

```bash
pytest tests --html=reports/report.html --self-contained-html
```

Generated artifacts:

- HTML report: `reports/report.html`
- Logs: `logs/test_execution.log`
- Failure screenshots: `screenshots/`

## Test Categories Explained

### UI

Validates that the chatbot loads, accepts input, sends messages, renders responses, clears the input, supports scrolling, and works in desktop and mobile contexts.

### AI Response Validation

Validates response completeness, structure, fallback detection, keyword relevance, and semantic alignment against the intended public-service topic.

### Multilingual

Checks English and Arabic response behavior, Arabic script presence, RTL compatibility, and intent consistency across both languages.

### Security

Covers XSS-style payloads, SQL-like strings, and prompt injection attempts to ensure the chatbot remains stable, safe, and on-domain.

### Performance

Measures end-to-end response latency from send action until a bot response is detected.

### Reliability

Repeats prompts and compares responses for semantic consistency and platform stability.

### Accessibility

Checks practical basics such as keyboard interaction, input discoverability, and accessible attributes on input and action controls.

## Assumptions And Limitations

- The framework targets the live beta environment, so occasional content and latency variation is expected.
- DOM selectors can evolve; the page object uses fallback locator strategies to reduce brittleness.
- Semantic similarity uses `all-MiniLM-L6-v2` as required. This is helpful but not a source-of-truth validator.
- Hallucination detection is heuristic-based and intentionally lightweight.
- No external truth-source API is used for factual verification.
- Because the application is live, transient failures may still occur due to environment or service instability.

## Future Improvements

- Add API mocking for faster and more deterministic lower-environment testing
- Add external truth-source validation for critical government facts
- Add CI/CD integration with GitHub Actions, Azure DevOps, or Jenkins
- Add visual regression snapshots for major UI states
- Extend accessibility automation beyond basics with axe-core and deeper WCAG coverage

## Suggested CI Commands

```bash
pip install -r requirements.txt
playwright install
pytest tests --html=reports/report.html --self-contained-html
```
