# Yalla’s Book Template

A composited book-markup framework and project template for creating books with [Typst](https://typst.app). This repository contains a ready-to-use book skeleton, component library, and a small Python-based build system that compiles Typst sources, applies ICC output profiles, converts embedded images when required, and writes rich PDF metadata.

This project is the default book template used by the [YAL](https://github.com/DemerNkardaz/YAL) utility. You can initialize a new book project using YAL (strongly recommended):

```bash
yal new book
```

## Quick overview

1. `build/build.py` is the build entry point. It:
	 - fetches missing assets declared in `assets/registry.yml`;
	 - loads configuration from `settings/layout.yml`, `settings/build.yml` and `meta/book.yml`;
	 - runs `typst compile main.typ -> main.pdf` (with optional `--pages`, `--pdf-standard`, and `layout-mode` flags);
	 - copies the raw PDF to the configured export directory and applies an ICC output intent using `pikepdf`;
	 - optionally converts embedded images to the target color space using Pillow + ImageCms;
	 - writes PRISM / XMP / DC metadata into the PDF and saves it as the final output.

2. Build modes (defined in `settings/build.yml`) control the target ICC profile, PDF standard, pages to export and other per-mode options.

3. The Typst source tree (`main.typ`, `book/`, `code/`) contains the document structure and reusable components. Edit these sources to change the book content and layout.

## Requirements

- Typst (the `typst` CLI) must be installed and available in `PATH`.
- Python 3.8+.
- Python packages: `pikepdf`, `Pillow`, `PyYAML`.
	- Install quickly with:

```bash
pip install pikepdf Pillow PyYAML
```

- System tools required by Python packages:
	- `qpdf` is required by `pikepdf` (install via your package manager or from https://qpdf.sourceforge.io/).
	- On some systems, Pillow's ImageCms may require Little CMS (`lcms2`) development libraries. If image color conversion fails, install or enable Little CMS.

## Repository structure

- `main.typ` — project entry Typst document.
- `book/` — book-level Typst fragments (front matter, pre-title, chapters).
- `code/` — component library and templates used by the Typst sources (reusable macros and fragments).
- `content/` — various files for content related to the book, e.g. bibliography, characters, etc.
- `assets/` — static assets and an `registry.yml` declaring remote assets to fetch (ICC profiles, etc.).
- `build/` — Python build entrypoint and helper modules:
	- `build.py` — orchestrates compilation and post-processing.
	- `modules/` — helper modules: `assets.py`, `icc.py`, `image_process.py`, `meta.py`, `log.py`, `i18n.py`, etc.
- `note/` — user’s notes.
- `schemas/` — YAML schemas for book metadata, styles, etc.
- `settings/` — YAML configuration for build modes, layout defaults, hyphenation, typography rules, etc.
- `style/` — built-in and user-defined styles for text.
- `meta/book.yml` — canonical book metadata (title, authors, publisher, ISBN, etc.).

## Configuration

- Edit `meta/book.yml` to set book metadata (title, author, publisher, ISBN, edition).
- Adjust `settings/layout.yml` for layout defaults and the default `mode` used when running the build without `--mode`.
- Define build modes in `settings/build.yml`. Each mode typically selects an ICC profile and PDF standard.

## Building the book

Examples:

```bash
# default build (uses mode from settings/layout.yml)
python build/build.py

# specify a mode (modes are defined in settings/build.yml)
python build/build.py --mode print
```

Or with using Makefile/YAL:

```bash
make

make m=print

#

yal make

yal make --mode print
```

Notes:
- The build script calls `typst compile main.typ main.pdf` and may pass `--pages` or `--pdf-standard` according to the selected mode.
- After compilation the script uses `pikepdf` to attach an OutputIntent (ICC profile) and write PDF metadata. If `settings/build.yml` enables `color-conversion`, embedded images are converted to the target color space.
- The script writes a log to `build/build.log`.

## Working on the content

- Edit `book/` files or `main.typ` to change structure and content.
- Add or modify reusable pieces in `code/extension/` and `book/template/`.
- Assets, fonts and ICC profiles live in `assets/`. Use `assets/registry.yml` to register remote assets — the build will download them automatically. Use `asset` fields in `meta/book.yml` to reference assets by name.

## Extending and customization

- Add new build modes in `settings/build.yml` to support different output profiles (e.g. print vs screen).
- Create new components in `code/` to share styles across books.

## Development notes

- Linting / formatting: follow the repository style for Typst and Python.
- The Python helpers are intentionally small and dependency-light; when adding features prefer to extend `build/modules/` rather than modifying `build.py`.
- To debug build messages, inspect `build/build.log` and `build/messages.yml` which contains i18n keys used by the build.

