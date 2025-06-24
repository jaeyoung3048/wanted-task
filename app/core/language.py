from collections.abc import Callable, Iterable, Iterator
from functools import cache
from typing import Any

import pycountry

from app.core.config import settings

__all__ = [
    "LANGUAGE_ALIAS_MAP",
    "LanguageCode",
    "choose_language",
    "normalize_language_code",
    "validate_language_code",
]

# ISO-639-1 과 다른 케이스 대응
LANGUAGE_ALIAS_MAP: dict[str, str] = {
    "jp": "ja",
    "tw": "zh-Hant",
    "kr": "ko",
    "cn": "zh",
}


@cache
def normalize_language_code(code: str | None) -> str | None:
    if not code or not isinstance(code, str):
        return None

    code_lower = code.lower()
    canonical = LANGUAGE_ALIAS_MAP.get(code_lower, code_lower)

    if len(canonical) == 2 and pycountry.languages.get(alpha_2=canonical):
        return canonical

    try:
        language = pycountry.languages.lookup(canonical)
    except LookupError:
        return None

    return getattr(language, "alpha_2", None) or canonical


def validate_language_code(code: str | None) -> bool:
    return normalize_language_code(code) is not None


def choose_language(available: Iterable[str], requested: str | None) -> str:
    available_set = {normalize_language_code(lang) or lang for lang in available}

    req_normalized = normalize_language_code(requested)
    if req_normalized and req_normalized in available_set:
        return req_normalized

    if _DEFAULT_LANG_CANON in available_set:
        return _DEFAULT_LANG_CANON

    return sorted(available_set)[0]


class LanguageCode(str):
    """언어코드 대응용 타입"""

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[Any], Any]]:
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        if normalize_language_code(v) is None:
            raise ValueError("Invalid language code")
        return v


_DEFAULT_LANG_CANON = normalize_language_code(settings.DEFAULT_LANGUAGE)

if _DEFAULT_LANG_CANON is None:
    raise ValueError(
        f"Invalid DEFAULT_LANGUAGE in settings: {settings.DEFAULT_LANGUAGE!r}"
    )
