import argparse
import json
import logging
import random
import time
from pathlib import Path

import requests

from availability import Availability, detect_availability
from config import load_config
from telegram_notifier import TelegramNotifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("afisha-ticket-bot")


def fetch_html(url: str, user_agent: str, timeout_seconds: int) -> str:
    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    response = requests.get(url, headers=headers, timeout=timeout_seconds)
    response.raise_for_status()
    return response.text


def load_state(state_file: str) -> dict:
    path = Path(state_file)
    if not path.exists():
        return {"last_status": None}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"last_status": None}


def save_state(state_file: str, state: dict) -> None:
    Path(state_file).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def check_once(config, notifier: TelegramNotifier, state: dict) -> dict:
    try:
        html = fetch_html(config.event_url, config.user_agent, config.request_timeout_seconds)
    except requests.RequestException as exc:
        log.warning("Failed to fetch event page: %s", exc)
        return state

    status = detect_availability(html)
    log.info("Current status: %s", status.value)

    last_status = state.get("last_status")
    if status is Availability.AVAILABLE and last_status != Availability.AVAILABLE.value:
        message = "🎟 Похоже, билеты появились в продаже!\n" + config.event_url
        try:
            notifier.send(message)
            log.info("Notification sent.")
        except requests.RequestException as exc:
            log.error("Failed to send Telegram notification: %s", exc)
            # Don't record the new status, so we retry the notification next time.
            return state

    state["last_status"] = status.value
    return state


def dump_html(config) -> None:
    html = fetch_html(config.event_url, config.user_agent, config.request_timeout_seconds)
    out_path = Path("page.html")
    out_path.write_text(html, encoding="utf-8")
    log.info("Saved page HTML to %s (%d bytes)", out_path, len(html))


def main() -> None:
    parser = argparse.ArgumentParser(description="Yandex Afisha ticket availability watcher")
    parser.add_argument("--once", action="store_true", help="Check once and exit, without looping")
    parser.add_argument(
        "--dump-html",
        action="store_true",
        help="Save the current event page HTML to page.html and exit (for tuning availability.py)",
    )
    args = parser.parse_args()

    config = load_config()

    if args.dump_html:
        dump_html(config)
        return

    notifier = TelegramNotifier(config.telegram_bot_token, config.telegram_chat_id)
    state = load_state(config.state_file)

    log.info("Watching: %s", config.event_url)

    if args.once:
        state = check_once(config, notifier, state)
        save_state(config.state_file, state)
        return

    while True:
        state = check_once(config, notifier, state)
        save_state(config.state_file, state)
        jitter = random.uniform(0.8, 1.2)
        time.sleep(config.check_interval_seconds * jitter)


if __name__ == "__main__":
    main()
