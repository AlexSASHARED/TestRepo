import re
from enum import Enum


class Availability(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


# Checked first, since a page can carry both a stale "buy" button in cached
# markup and a clear banner saying there's nothing to sell.
UNAVAILABLE_PATTERNS = [
    r"билетов\s+нет",
    r"нет\s+в\s+продаже",
    r"продажа\s+(билетов\s+)?завершена",
    r"распродано",
    r"мероприятие\s+отменено",
    r"мероприятие\s+перенесено",
    r"продажи?\s+(ещё|еще)\s+не\s+начал",
    r"скоро\s+в\s+продаже",
]

AVAILABLE_PATTERNS = [
    r"купить\s+билет",
    r"выбрать\s+места",
    r"добавить\s+в\s+корзину",
    r"в\s+продаже",
]


def _search_any(patterns, text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def extract_visible_text(html: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def detect_availability(html: str) -> Availability:
    """Best-effort detection of ticket availability from page markup.

    Yandex Afisha's markup can change at any time; if this starts always
    returning UNKNOWN, run `python bot.py --dump-html page.html` and adjust
    the patterns above to match what the page currently says.
    """
    text = extract_visible_text(html)

    if _search_any(UNAVAILABLE_PATTERNS, text):
        return Availability.UNAVAILABLE
    if _search_any(AVAILABLE_PATTERNS, text):
        return Availability.AVAILABLE
    return Availability.UNKNOWN
