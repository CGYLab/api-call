"""Shared configuration for API testing tools."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Config directory in current working directory
CONFIG_DIR = Path.cwd() / ".claude" / "api-testing"

# .env template
ENV_TEMPLATE = """# API Testing Configuration
# Documentation: https://github.com/CGYLab/api-call

# Base Settings
PORT=3000
AUTH_MODE=jwt  # jwt | api-key | basic | none

# JWT Mode
# API_TEST_EMAIL=user@example.com
# API_TEST_PASSWORD=yourpassword
# AUTH_LOGIN_ENDPOINT=/auth/login
# AUTH_REFRESH_ENDPOINT=/auth/refresh

# API Key Mode
# API_KEY=your-api-key-here
# API_KEY_HEADER=X-API-Key

# Basic Auth Mode
# BASIC_AUTH_USERNAME=admin
# BASIC_AUTH_PASSWORD=password
"""


def ensure_setup() -> bool:
    """
    Auto-setup on first run.

    Returns:
        True if setup exists and ready to proceed.
        False if setup just created (caller should exit).
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Create .gitignore
    gitignore = CONFIG_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(".env\ntokens.jsonl\n")

    # Create .env from template
    env_file = CONFIG_DIR / ".env"
    if not env_file.exists():
        env_file.write_text(ENV_TEMPLATE)
        print(f"Created config directory: {CONFIG_DIR}")
        print(f"Created .env file: {env_file}")
        print(f"Created .gitignore")
        print()
        print("Please edit .claude/api-testing/.env with your settings, then run again.")
        return False

    return True


def require_setup() -> None:
    """Ensure setup exists, exit if just created."""
    if not ensure_setup():
        sys.exit(0)


# Load .env from config directory
env_file = CONFIG_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)

# API Configuration
PORT = os.getenv("PORT", "3000")
BASE_URL = f"http://localhost:{PORT}/api/v1"

# Auth Mode: jwt, api-key, basic, none
AUTH_MODE = os.getenv("AUTH_MODE", "jwt").lower()

# Auth Endpoints (for JWT mode)
AUTH_LOGIN_ENDPOINT = os.getenv("AUTH_LOGIN_ENDPOINT", "/auth/login")
AUTH_REFRESH_ENDPOINT = os.getenv("AUTH_REFRESH_ENDPOINT", "/auth/refresh")

# JWT Mode - Test credentials (optional - can be overridden via CLI)
DEFAULT_EMAIL = os.getenv("API_TEST_EMAIL")
DEFAULT_PASSWORD = os.getenv("API_TEST_PASSWORD")

# API Key Mode
API_KEY = os.getenv("API_KEY")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")

# Basic Auth Mode
BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")

# Token storage - in config directory
TOKEN_FILE = CONFIG_DIR / "tokens.jsonl"
