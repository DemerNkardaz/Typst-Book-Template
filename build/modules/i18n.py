from pathlib import Path
import locale
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
MESSAGES_YML = BASE_DIR / "build" / "messages.yml"

locale_name = locale.getdefaultlocale()[0] or locale.getlocale()[0] or "en"
_lang = locale_name.split("_")[0]

with open(MESSAGES_YML, encoding="utf-8") as f:
    _messages = yaml.safe_load(f)

_locale = _messages.get(_lang) or _messages["en"]


def msg(key: str, **kwargs) -> str:
    category, name = key.split(".", 1)
    template = _locale.get(category, {}).get(name, key)
    return template.format(**kwargs) if kwargs else template


def info(key: str, **kwargs) -> None:
    print(msg(key, **kwargs))


def success(key: str, **kwargs) -> None:
    print(f"\033[1;32m{msg(key, **kwargs)}\033[0m")


def succes(key: str, **kwargs) -> None:
    success(key, **kwargs)


def warn(key: str, **kwargs) -> None:
    print(f"\033[1;33m{msg(key, **kwargs)}\033[0m")


def error(key: str, **kwargs) -> str:
    return msg(key, **kwargs)
