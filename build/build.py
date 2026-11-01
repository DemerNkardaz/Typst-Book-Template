import io
import subprocess
import sys
import yaml
from pathlib import Path
import pikepdf
import shutil
import argparse

from modules.assets import fetch_assets
from modules.icc import apply_output_intent, get_color_channels, pdf_info
from modules.image_process import convert_images
from modules.log import write_log
from modules.meta import write_pdf_metadata
from modules.pdf_validation import VeraPdfError, VeraPdfUnavailable, validate_pdf
from modules.i18n import error, info, succes, warn

parser = argparse.ArgumentParser()
parser.add_argument("--mode")
parser.add_argument("--as", dest="format")
args = parser.parse_args()

BASE_DIR = Path(__file__).parent.parent

if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

fetch_assets()

LAYOUT_YML = BASE_DIR / "settings" / "layout.yml"
BUILD_YML = BASE_DIR / "settings" / "build.yml"
BOOK_YML = BASE_DIR / "meta" / "book.yml"
ICC_DIR = BASE_DIR / "assets" / "ICC"
MAIN_TYP = BASE_DIR / "main.typ"
LOG_PATH = BASE_DIR / "build/build.log"

with open(LAYOUT_YML, encoding="utf-8") as f:
    layout = yaml.safe_load(f)

with open(BUILD_YML, encoding="utf-8") as f:
    build = yaml.safe_load(f)

with open(BOOK_YML, encoding="utf-8") as f:
    meta = yaml.safe_load(f)

book = meta.get("book", {})
publisher = meta.get("publisher", {})
contributor = meta.get("contributor", {})
version = meta.get("version", {})
status = meta.get("status", {})
date = meta.get("date", {})
copyright = meta.get("copyright", {})
prop = meta.get("property", {})

_authors = meta.get("author", [])
author = (
    _authors[0]
    if isinstance(_authors, list) and _authors
    else _authors if isinstance(_authors, dict)
    else {}
)

if status.get("stage") == "draft":
    warn("warnings.status-draft")

mode = args.mode or layout["mode"]
mode_config = build[f"mode-{mode}"]
output_format = args.format or "pdf"
if output_format not in {"pdf", "png"}:
    parser.error("--as must be either pdf or png")

output_name = (
    build["output-file-name"]
    if build.get("output-file-name") and build["output-file-name"] is not None
    else book["title"]
)

icc_name = mode_config["ICC"]
output_condition_identifier = mode_config.get("output-condition-identifier", icc_name)
output_condition = mode_config.get("output-condition")
output_registry = mode_config.get("output-registry")
pdf_version_raw = mode_config.get("pdf-version")
pdf_validator_raw = mode_config.get("pdf-validator")
color_conversion = bool(build.get("color-conversion", False))
pdf_validator_values = (
    pdf_validator_raw if isinstance(pdf_validator_raw, list) else [pdf_validator_raw]
)
post_validation_standards = [
    standard
    for standard in pdf_validator_values
    if isinstance(standard, str) and standard.startswith(("PDF/A-", "PDF/UA-"))
]
is_pdfa = pdf_version_raw is not None and pdf_version_raw.startswith("PDF/A-")
is_pdfa = is_pdfa or any(
    isinstance(standard, str) and standard.startswith("PDF/A-")
    for standard in pdf_validator_values
)

pdf_version_to_standard = {
    "PDF 1.4": "1.4",
    "PDF 1.5": "1.5",
    "PDF 1.6": "1.6",
    "PDF 1.7": "1.7",
    "PDF 2.0": "2.0",
    "PDF/A-1b": "a-1b",
    "PDF/A-1a": "a-1a",
    "PDF/A-2b": "a-2b",
    "PDF/A-2u": "a-2u",
    "PDF/A-2a": "a-2a",
    "PDF/A-3b": "a-3b",
    "PDF/A-3u": "a-3u",
    "PDF/A-3a": "a-3a",
    "PDF/A-4": "a-4",
    "PDF/A-4f": "a-4f",
    "PDF/A-4e": "a-4e",
    "PDF/UA-1": "ua-1",
}

pdf_standard = (
    pdf_version_to_standard.get(pdf_version_raw)
    if isinstance(pdf_version_raw, str)
    else None
)
standards_list = [pdf_standard] if pdf_standard else []

if isinstance(pdf_validator_raw, list):
    for v in pdf_validator_raw:
        val = pdf_version_to_standard.get(v)
        if val:
            standards_list.append(val)
elif isinstance(pdf_validator_raw, str):
    val = pdf_version_to_standard.get(pdf_validator_raw)
    if val:
        standards_list.append(val)

pdf_standard = ",".join(standards_list)

export_dir = (
    BASE_DIR / build["export-dir"]
    if build.get("export-dir")
    else BASE_DIR
)

if export_dir != BASE_DIR:
    export_dir.mkdir(parents=True, exist_ok=True)

raw_pdf_path = BASE_DIR / "main.pdf"
pdf_path = export_dir / f"{output_name} [{mode}].pdf"
png_path = export_dir / f"{output_name} [{mode}]{{p}}.png"
icc_path = ICC_DIR / f"{icc_name}.icc"

compile_output = png_path if output_format == "png" else raw_pdf_path
info("info.typst-compiling", src=MAIN_TYP, dst=compile_output)
typst_cmd = ["typst", "compile", str(MAIN_TYP), str(compile_output)]

if output_format == "png":
    typst_cmd += ["--format", "png", "--ppi", str(build.get("png-ppi", 300))]
elif pdf_standard:
    typst_cmd += ["--pdf-standard", pdf_standard]

pages = mode_config.get("pages")
if isinstance(pages, list):
    pages = ",".join(map(str, pages))
if pages is not None:
    typst_cmd += ["--pages", str(pages)]
if args.mode is not None:
    typst_cmd += ["--input", f"layout-mode={mode}"]

result = subprocess.run(typst_cmd, text=True)

if result.returncode != 0:
    if result.stdout:
        print("", result.stdout)
    if result.stderr:
        print("", result.stderr)
    raise SystemExit(error("errors.typst-failed"))
succes("info.typst-done")

if output_format == "png":
    info("info.png-exported", path=png_path)
    raise SystemExit(0)

pdf_standard_label = pdf_version_raw or "—"
info("info.icc-using", icc=icc_name, mode=mode, standard=pdf_standard_label)

with open(icc_path, "rb") as f:
    icc_data = f.read()

channels = get_color_channels(icc_data)
raw_info = pdf_info(raw_pdf_path)
shutil.copy2(raw_pdf_path, pdf_path)
with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
    if color_conversion:
        converted, skipped = convert_images(pdf, icc_data, channels)
        info("info.cc-converted", n=converted)
        if skipped:
            warn("warnings.cc-skipped", n=skipped)

    apply_output_intent(
        pdf,
        icc_data,
        channels,
        output_condition_identifier,
        output_condition=output_condition,
        registry_name=output_registry,
        is_pdfa=is_pdfa,
    )
    write_pdf_metadata(
        pdf,
        book,
        publisher,
        prop,
        version,
        copyright,
        author,
    )
    pdf.save(pdf_path)

info("info.icc-applied", path=pdf_path)

for standard in post_validation_standards:
    try:
        validate_pdf(pdf_path, standard)
    except VeraPdfUnavailable:
        raise SystemExit(error("errors.verapdf-not-found"))
    except VeraPdfError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(error("errors.verapdf-failed"))
    succes("info.verapdf-passed", standard=standard, path=pdf_path)

if build.get("open-after-build", False):
    CREATE_BREAKAWAY_FROM_JOB = 0x01000000
    subprocess.Popen(
        ["cmd", "/c", "start", "", str(pdf_path)],
        shell=False,
        creationflags=(
            subprocess.DETACHED_PROCESS | CREATE_BREAKAWAY_FROM_JOB
        ),
    )

out_info = pdf_info(pdf_path)

write_log(LOG_PATH, raw_pdf_path, pdf_path, raw_info, out_info)
