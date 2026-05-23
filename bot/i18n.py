from bot.config.settings import Settings
from bot.lang.en import _STRINGS_EN
from bot.lang.es import _STRINGS_ES

_STRINGS = {
    "en": _STRINGS_EN,
    "es": _STRINGS_ES,
}


def _(key: str, lang: str = None, **kwargs) -> str:
    if lang is None:
        lang = Settings.DEFAULT_LANG
    text = _STRINGS.get(lang, _STRINGS[Settings.DEFAULT_LANG]).get(key, "")
    if not text:
        text = _STRINGS[Settings.DEFAULT_LANG].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def get_available_langs() -> list:
    return list(_STRINGS.keys())
