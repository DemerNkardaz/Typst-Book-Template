# 🍰

Приветствую тебя в шаблон для создания книги! [Я](https://github.com/DemerNkardaz) создаю его по большей части для своих проектов, но рада видеть тебя здесь! Надеюсь, тебе этот шаблон будет полезен.

Welcome to the template for creating a book! [I](https://github.com/DemerNkardaz) create it mostly for my projects, but glad to see you here! I hope this template will be useful to you.

## Сборки книги

В корне шаблона расположен файл `build.py` — он необходим для более точной настройки выходного `*.pdf` файла, так как typst не может реализовать вообще всё.

Для использования этого скрипта убедись, что у тебя есть следующие пакеты:

- `pikepdf`
- `pillow`
- `pyyaml`
- Версия python не ниже 3.14 (использовалась при создании этого шаблона)

Если этих пакетов нет, установите их с помощью `pip`:

```bash
pip install pyyaml pikepdf pillow
```
Если ты используешь VS Code, то для сборки книги достаточно будет нажать <kbd>F5</kbd> или использовать команду `make`/`make m=<режим>` в терминале.

## Рекомендации

- Используйте изображения, соответствующие целевым ICC-профилям и целевому цвету (RGB/CMYK).

---

## Book assemblies

In the root of the template is a file `build.py` — it is necessary for a more accurate output `*.pdf` file, because typst cannot implement everything.

To use this script, make sure you have the following packages:

- `pikepdf`
- `pillow`
- `pyyaml`
- Python version 3.14 or higher (used when creating this template)

If these packages are not installed, install them with `pip`:

```bash
pip install pyyaml pikepdf pillow
```
If you use VS Code, you can build the book by pressing <kbd>F5</kbd> or using the `make`/`make m=<mode>` command in the terminal.

## Recommendations

- Use images that match the target ICC profiles and target color (RGB/CMYK).
