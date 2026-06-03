from pathlib import Path
from i18n import load_locale

def get_next_number(chapters_dir):
    existing = [f.name.split(']')[0].replace('[', '') for f in chapters_dir.glob("*.typ") if ']' in f.name]
    numbers = [int(n) for n in existing if n.isdigit()]
    return max(numbers) + 1 if numbers else 1

def main():
    root_dir = Path(__file__).parent.parent.parent
    chapters_dir = root_dir / "book" / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    locale_data, _ = load_locale()
    texts = locale_data.get('py', {}).get('add-chapter', {})

    num_input = input(f"[YAL] {texts.get('number', 'Enter number')}: ").strip()
    number = int(num_input) if num_input.isdigit() else get_next_number(chapters_dir)

    name = input(f"[YAL] {texts.get('name', 'Enter name')}: ").strip()

    filename = f"[{number}] {name}.typ"
    file_path = chapters_dir / filename

    content = f"""#import "../preamble.typ": *

== {number}. {name}

"""

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[YAL] {texts.get('created', 'Created chapter')}: book/chapters/{filename}")

if __name__ == "__main__":
    main()
