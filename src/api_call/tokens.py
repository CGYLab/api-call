"""Token management using JSONL storage."""

import json
from datetime import datetime, timedelta
from typing import Optional

from .config import TOKEN_FILE, CONFIG_DIR


def save_tokens(
    access_token: str,
    refresh_token: str,
    expires_in: int,
    user_email: str,
    user_id: str,
) -> None:
    """Save tokens to JSONL file."""
    # Ensure config directory exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    expires_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat()

    entry = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": expires_in,
        "user_email": user_email,
        "user_id": user_id,
        "timestamp": timestamp,
        "expires_at": expires_at,
    }

    # Append to JSONL file
    with open(TOKEN_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_latest_token() -> Optional[dict]:
    """Load the most recent token entry from JSONL."""
    if not TOKEN_FILE.exists():
        return None

    last_entry = None
    with open(TOKEN_FILE, "r") as f:
        for line in f:
            if line.strip():
                last_entry = json.loads(line)

    return last_entry


def load_valid_token() -> Optional[dict]:
    """Load a valid (non-expired) token entry."""
    entry = load_latest_token()
    if not entry:
        return None

    expires_at = datetime.fromisoformat(entry["expires_at"])
    # Add 30 second buffer for expiration
    if datetime.now() + timedelta(seconds=30) >= expires_at:
        return None

    return entry


def is_token_expired(entry: dict) -> bool:
    """Check if a token entry is expired."""
    if not entry:
        return True

    expires_at = datetime.fromisoformat(entry["expires_at"])
    # Add 30 second buffer
    return datetime.now() + timedelta(seconds=30) >= expires_at
