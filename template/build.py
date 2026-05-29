import subprocess
import yaml
from pathlib import Path
import pikepdf
from pikepdf import Dictionary, Array, Name, Stream

BASE_DIR = Path(__file__).parent
LAYOUT_YML = BASE_DIR / "settings" / "layout.yml"
BUILD_YML = BASE_DIR / "settings" / "build.yml"
ICC_DIR = BASE_DIR / "assets" / "ICC"
MAIN_TYP = BASE_DIR / "main.typ"

with open(LAYOUT_YML, encoding="utf-8") as f:
    layout = yaml.safe_load(f)

with open(BUILD_YML, encoding="utf-8") as f:
    build = yaml.safe_load(f)

mode = layout["mode"]
mode_config = build[f"mode-{mode}"]

output_name = build["output-file-name"]
icc_name = mode_config["ICC"]
gts_raw = mode_config.get("GTS")

gts_map = {
    "PDF/A": "/GTS_PDFA1",
    "PDF/X": "/GTS_PDFX",
}
intent_s = gts_map.get(gts_raw, "/GTS_PDFXUnknown")

pdf_path = BASE_DIR / f"{output_name}.pdf"
icc_path = ICC_DIR / f"{icc_name}.icc"

print(f"[typst] компилируем {MAIN_TYP} → {pdf_path}")
result = subprocess.run(
    ["typst", "compile", str(MAIN_TYP), str(pdf_path)],
    capture_output=True,
    text=True,
)
if result.returncode != 0:
    print(result.stderr)
    raise SystemExit("typst завершился с ошибкой")
print("[typst] готово")

gts_label = gts_raw or "Unknown"
print(f"[icc] встраиваем {icc_name} (mode: {mode}, GTS: {gts_label})")

with open(icc_path, "rb") as f:
    icc_data = f.read()

color_space_tag = icc_data[16:20].decode("ascii", errors="ignore").strip()
channels = {"CMYK": 4, "RGB": 3, "GRAY": 1}.get(color_space_tag, 3)

with pikepdf.open(pdf_path) as pdf:
    icc_stream = Stream(pdf, icc_data)
    icc_stream["/N"] = channels

    output_intent = Dictionary(
        Type=Name("/OutputIntent"),
        S=Name(intent_s),
        OutputConditionIdentifier=pikepdf.String(icc_name),
        DestOutputProfile=icc_stream,
    )

    pdf.Root["/OutputIntents"] = Array([pdf.make_indirect(output_intent)])
    pdf.save(pdf_path)

print(f"[icc] сохранено → {pdf_path}")
