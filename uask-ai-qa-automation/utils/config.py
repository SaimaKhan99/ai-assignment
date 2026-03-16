"""Central configuration for the U-Ask automation framework."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BASE_URL = os.getenv("UASK_BASE_URL", "https://beta-ask.u.ae/en/uask")
DEFAULT_TIMEOUT = int(os.getenv("UASK_DEFAULT_TIMEOUT_MS", "30000"))
RESPONSE_TIMEOUT_SECONDS = int(os.getenv("UASK_RESPONSE_TIMEOUT_SECONDS", "30"))
STRICT_RESPONSE_TIME_SECONDS = float(
    os.getenv("UASK_STRICT_RESPONSE_TIME_SECONDS", "10")
)
SOFT_RESPONSE_TIME_SECONDS = float(
    os.getenv("UASK_SOFT_RESPONSE_TIME_SECONDS", "10")
)
SEMANTIC_SIMILARITY_THRESHOLD = float(
    os.getenv("UASK_SEMANTIC_SIMILARITY_THRESHOLD", "0.45")
)
CONSISTENCY_SIMILARITY_THRESHOLD = float(
    os.getenv("UASK_CONSISTENCY_SIMILARITY_THRESHOLD", "0.55")
)

DEFAULT_DESKTOP_VIEWPORT = {"width": 1440, "height": 1024}
DEFAULT_MOBILE_DEVICE = os.getenv("UASK_MOBILE_DEVICE", "iPhone 13")

SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"
LOG_DIR = PROJECT_ROOT / "logs"
REPORT_DIR = PROJECT_ROOT / "reports"
LOG_FILE_PATH = LOG_DIR / "test_execution.log"
TEST_DATA_PATH = PROJECT_ROOT / "testdata" / "test-data.json"

SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
