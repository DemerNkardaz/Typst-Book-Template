import yaml
import locale
from pathlib import Path

LOCALE_DIR = Path(__file__).parent.parent.parent / "settings" / "locale"

def get_system_lang():
    try:
        default_locale = locale.getdefaultlocale()[0] or "en"
        return default_locale.split("_")[0]
    except Exception:
        return "en"

def get_available_languages():
    return [f.stem for f in LOCALE_DIR.glob("*.yml")]

def load_locale(lang=None):
    langs = get_available_languages()

    target_lang = lang or get_system_lang()

    if target_lang not in langs:
        target_lang = 'en'

    file_path = LOCALE_DIR / f"{target_lang}.yml"

    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return data, target_lang
