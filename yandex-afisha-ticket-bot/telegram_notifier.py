import requests


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str, timeout_seconds: int = 15):
        self._api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id
        self._timeout_seconds = timeout_seconds

    def send(self, text: str) -> None:
        response = requests.post(
            self._api_url,
            json={
                "chat_id": self._chat_id,
                "text": text,
                "disable_web_page_preview": False,
            },
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
