import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    event_url: str
    telegram_bot_token: str
    telegram_chat_id: str
    check_interval_seconds: int
    request_timeout_seconds: int
    user_agent: str
    state_file: str


def load_config() -> Config:
    event_url = os.environ.get("EVENT_URL", "").strip()
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    missing = [
        name
        for name, value in (
            ("EVENT_URL", event_url),
            ("TELEGRAM_BOT_TOKEN", telegram_bot_token),
            ("TELEGRAM_CHAT_ID", telegram_chat_id),
        )
        if not value
    ]
    if missing:
        raise SystemExit(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env and fill them in."
        )

    return Config(
        event_url=event_url,
        telegram_bot_token=telegram_bot_token,
        telegram_chat_id=telegram_chat_id,
        check_interval_seconds=int(os.environ.get("CHECK_INTERVAL_SECONDS", "90")),
        request_timeout_seconds=int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "15")),
        user_agent=os.environ.get(
            "USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        ),
        state_file=os.environ.get("STATE_FILE", "state.json"),
    )
