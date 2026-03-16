# U-Ask AI QA Automation Framework

## Overview

This repository contains a production-style end-to-end QA automation framework for the UAE Government generative AI assistant, U-Ask.

Target application:

- `https://beta-ask.u.ae/en/uask`

The framework is designed to validate:

- Chatbot UI behavior
- AI response quality and structure
- English and Arabic behavior
- Prompt injection resistance
- XSS-style and suspicious input handling
- Lightweight hallucination heuristics
- Reliability and semantic consistency
- Response latency
- Basic accessibility behavior
- Logs, screenshots, and HTML reporting

## Why AI Testing Is Different

Traditional UI and API tests usually validate deterministic outputs. LLM-based systems are different:

- Responses can vary in wording while still being correct.
- Exact string matching is often the wrong assertion strategy.
- A response may look fluent but still be irrelevant or partially wrong.
- Security validation must include adversarial prompting, not just malformed payloads.
- Reliability must be measured through relevance, stability, and semantic consistency.

To reflect that, this framework combines multiple layers of validation:

- Non-empty response checks
- Structural sanity checks
- Keyword relevance checks
- Semantic similarity using `all-MiniLM-L6-v2`
- Heuristic hallucination detection
- Security-focused guardrail checks

## Tech Stack

- Python `3.11+`
- `pytest`
- `playwright`
- `pytest-html`
- `sentence-transformers`
- `torch`
- `numpy`

## Framework Design

The framework is organized around:

- Page Object Model for resilient live-site interaction
- Validator classes for AI-specific assertions
- Utility modules for logging, screenshots, language handling, and timing
- JSON-driven test data
- Shared pytest fixtures for browser reuse

Key design decisions:

- Fallback selectors are used because the target is a live beta site.
- Assertions are tolerant to wording variation.
- Failure artifacts are captured automatically.
- Config values are centralized in `utils/config.py`.
- The current live flow includes auto-handling for the disclaimer modal.
- Response-driven tests skip when the live site presents reCAPTCHA, because that blocks automation rather than indicating a product failure.

## Project Structure

```text
uask-ai-qa-automation/
├── pages/
│   └── chatbot_page.py
├── testdata/
│   └── test-data.json
├── tests/
│   ├── conftest.py
│   ├── test_accessibility.py
│   ├── test_ai_responses.py
│   ├── test_multilingual.py
│   ├── test_performance.py
│   ├── test_reliability.py
│   ├── test_security.py
│   └── test_ui_behavior.py
├── utils/
│   ├── config.py
│   ├── language_utils.py
│   ├── logger.py
│   ├── performance_utils.py
│   └── screenshot_utils.py
├── validators/
│   ├── hallucination_detector.py
│   ├── response_validator.py
│   ├── security_validator.py
│   └── semantic_validator.py
├── logs/
├── reports/
├── screenshots/
├── requirements.txt
└── README.md
```

## Test Coverage

### UI behavior

Validates:

- Page load
- Input visibility and readiness
- Sending a message
- Bot response rendering
- Input clearing
- Scroll behavior
- Mobile view load

### AI response validation

Validates:

- Response presence
- Readability and structure
- Fallback response detection
- Intent keyword relevance
- Semantic alignment to expected intent

### Multilingual validation

Validates:

- Arabic response behavior
- Arabic script presence
- RTL direction support
- Cross-language consistency between English and Arabic prompts

### Security validation

Validates:

- XSS-style payload handling
- SQL-like string handling
- Prompt injection resistance
- Raw HTML rendering avoidance

### Performance validation

Validates:

- End-to-end response latency against configured thresholds

### Reliability validation

Validates:

- Repeated-query consistency
- Relevance across repeated responses
- Continued input usability

### Accessibility validation

Validates:

- Input discoverability
- Keyboard flow around the send action
- Keyboard-based submission behavior

## Prerequisites

You need:

- Python `3.11+`
- Internet access to the live U-Ask beta site
- Ability to download Playwright browser binaries
- Enough disk and memory for `torch` and `sentence-transformers`

Important environment note:

- Use `python3.11` explicitly if your machine defaults to an older Python.
- Use `PYTHONPATH=.` when running `pytest`, because the repository imports local folders such as `pages` and `validators` directly.

## Setup

From the repository root:

```bash
cd uask-ai-qa-automation
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
export PYTHONPATH=.
```

## Run The Tests

### Collect tests only

Useful to verify imports and discovery:

```bash
pytest --collect-only -q
```

### Run the full suite

```bash
pytest tests --html=reports/report.html --self-contained-html
```

### Run individual test files

```bash
pytest tests/test_ui_behavior.py
pytest tests/test_ai_responses.py
pytest tests/test_multilingual.py
pytest tests/test_security.py
pytest tests/test_performance.py
pytest tests/test_reliability.py
pytest tests/test_accessibility.py
```

### Run a single test

```bash
pytest tests/test_ui_behavior.py::test_chat_page_loads -q
```

## Reports And Artifacts

Generated outputs:

- HTML report: `reports/report.html`
- Execution log: `logs/test_execution.log`
- Failure screenshots: `screenshots/`

## Configuration

Runtime values are controlled in `utils/config.py`.

Supported environment variables:

- `UASK_BASE_URL`
- `UASK_DEFAULT_TIMEOUT_MS`
- `UASK_RESPONSE_TIMEOUT_SECONDS`
- `UASK_STRICT_RESPONSE_TIME_SECONDS`
- `UASK_SOFT_RESPONSE_TIME_SECONDS`
- `UASK_SEMANTIC_SIMILARITY_THRESHOLD`
- `UASK_CONSISTENCY_SIMILARITY_THRESHOLD`
- `UASK_MOBILE_DEVICE`

Example:

```bash
export UASK_RESPONSE_TIMEOUT_SECONDS=45
export UASK_SEMANTIC_SIMILARITY_THRESHOLD=0.40
pytest tests/test_ai_responses.py
```

## Current Live-Site Behavior Handled By The Framework

The current automation includes workarounds for live-site behavior that can interfere with tests:

- Disclaimer modal is detected and accepted automatically.
- User message extraction waits briefly for the transcript to update.
- Response-dependent tests skip when visible reCAPTCHA blocks automation.

These are live-environment concerns, not application-code concerns inside this repository.

## Challenges Faced

The following issues were encountered while building and stabilizing the framework against the live site:

### 1. Live disclaimer modal blocked initial interaction

The chatbot now presents a disclaimer before interaction. Early selectors looked valid because the chat UI was rendered in the background, but the modal still intercepted clicks.

How it was handled:

- Added modal detection and automatic acceptance before interacting with the page.
- Added defensive checks before input and send actions.

### 2. Local import path issue during pytest execution

Running plain `pytest` did not always resolve local imports such as `pages` and `validators`.

How it was handled:

- Standardized execution with `PYTHONPATH=.`.
- Documented the requirement in this README.

### 3. Python version mismatch across environments

Some environments had `python3` pointing to Python `3.10`, while the project dependencies and runtime expectations align better with Python `3.11+`.

How it was handled:

- Documented use of `python3.11`.
- Recommended a dedicated virtual environment.

### 4. Playwright browser binaries were not installed by default

Even when the Python package was installed, Playwright could not launch Chromium until the browser binary was downloaded.

How it was handled:

- Added explicit `python -m playwright install chromium` to setup instructions.

### 5. Live-site selector drift

Because the target is a live beta site, some selectors and interaction timing are unstable.

How it was handled:

- Used fallback selectors in the page object.
- Added readiness and transcript polling where the UI updates asynchronously.

### 6. reCAPTCHA challenge on bot response submission

The live site sometimes presents reCAPTCHA after a prompt is submitted. This blocks response automation and can cause false failures if treated as a product issue.

How it was handled:

- Added reCAPTCHA detection.
- Response-based tests skip instead of failing with misleading timeout errors.

### 7. LLM nondeterminism

The chatbot does not always return identical wording for the same prompt.

How it was handled:

- Avoided exact string matching for core validations.
- Used semantic similarity, structure checks, and keyword presence instead.

### 8. Latency and environment variability

The live beta environment can have network delays, fluctuating response times, or temporary instability.

How it was handled:

- Centralized timeout configuration.
- Captured logs and screenshots for debugging.
- Kept assertions tolerant where appropriate.

## Assumptions And Limitations

- The framework targets a live beta environment, so transient failures can still happen.
- Some response-oriented tests may skip when reCAPTCHA blocks automation.
- Semantic similarity is useful for intent validation, but it is not a source of truth.
- Hallucination detection is heuristic-based.
- No external truth-source API is used for factual validation.
- Selector drift is always possible on a live site.

## Suggested Verification Flow

If you want a practical local run order, use:

```bash
pytest tests/test_ui_behavior.py -q
pytest tests/test_accessibility.py -q
pytest tests/test_ai_responses.py -q
pytest tests/test_multilingual.py -q
pytest tests/test_security.py -q
pytest tests/test_performance.py -q
pytest tests/test_reliability.py -q
```

This gives faster feedback on setup and interaction issues before running the full suite.

## Future Improvements

- Add CI workflow for automated scheduled runs
- Add structured test markers such as `smoke`, `live`, `security`, and `accessibility`
- Add richer reporting for skip reasons
- Add lower-environment or mocked execution mode to avoid reCAPTCHA
- Add API-level validation if service endpoints become available
- Extend accessibility checks with `axe-core`
- Add screenshot or visual regression coverage for major UI states

## Suggested CI Commands

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
export PYTHONPATH=.
pytest tests --html=reports/report.html --self-contained-html
```
