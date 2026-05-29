import io
import subprocess
import sys
import yaml
from pathlib import Path
import pikepdf
from pikepdf import Dictionary, Array, Name, Stream
from datetime import datetime
import shutil

if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent
LAYOUT_YML = BASE_DIR / "settings" / "layout.yml"
BUILD_YML = BASE_DIR / "settings" / "build.yml"
ICC_DIR = BASE_DIR / "assets" / "ICC"
MAIN_TYP = BASE_DIR / "main.typ"
LOG_PATH = BASE_DIR / "build.log"


def pdf_info(path: Path) -> dict[str, object]:
    info: dict[str, object] = {"size_bytes": path.stat().st_size}
    with pikepdf.open(path) as pdf:
        info["pages"] = len(pdf.pages)
        info["pdf_version"] = str(pdf.pdf_version)

        docinfo = pdf.docinfo
        for key in (
            "/Title",
            "/Author",
            "/Creator",
            "/Producer",
            "/CreationDate",
            "/ModDate",
        ):
            val = docinfo.get(key)
            info[key.strip("/")] = str(val) if val else None

        intents = pdf.Root.get("/OutputIntents")
        if intents:
            intent = intents[0]
            icc_info: dict[str, object] = {
                "S": str(intent.get("/S")),
                "OutputConditionIdentifier":
                    str(intent.get("/OutputConditionIdentifier")),
            }
            profile = intent.get("/DestOutputProfile")
            if profile:
                data = bytes(profile.read_bytes())
                tag = data[16:20].decode("ascii", errors="ignore").strip()
                icc_info["color_space"] = tag
                icc_info["size_bytes"] = len(data)
            info["OutputIntent"] = icc_info
        else:
            info["OutputIntent"] = None

    return info


def write_log(
    raw_path: Path,
    out_path: Path,
    raw_info: dict[str, object],
    out_info: dict[str, object],
) -> None:
    def fmt_size(b: object) -> str:
        if not isinstance(b, int):
            return "—"
        return f"{b:,} bytes ({b / 1024 / 1024:.2f} MB)"

    def section(path: Path, info: dict[str, object]) -> str:
        name = path.name.upper()
        sep = "=" * len(name)
        lines = [
            f"| {sep}",
            f"| {name}",
            f"| {sep}",
            f"path:        {path}",
            f"size:        {fmt_size(info['size_bytes'])}",
            f"pages:       {info['pages']}",
            f"pdf version: {info['pdf_version']}",
            f"title:       {info.get('Title') or '—'}",
            f"author:      {info.get('Author') or '—'}",
            f"creator:     {info.get('Creator') or '—'}",
            f"producer:    {info.get('Producer') or '—'}",
            f"created:     {info.get('CreationDate') or '—'}",
            f"modified:    {info.get('ModDate') or '—'}",
        ]
        icc = info["OutputIntent"]
        if isinstance(icc, dict):
            lines += [
                f"icc profile: {icc.get('OutputConditionIdentifier')}",
                f"icc gts:     {icc.get('S')}",
                f"icc space:   {icc.get('color_space', '—')}",
                f"icc size:    {fmt_size(icc.get('size_bytes'))}",
            ]
        else:
            lines.append("icc profile: not yet assigned")
        return "\n".join(lines)

    content = "\n\n".join([
        f"build log — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        section(raw_path, raw_info),
        section(out_path, out_info),
    ])

    LOG_PATH.write_text(content + "\n", encoding="utf-8")
    print(f"[log] {LOG_PATH}")


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

raw_pdf_path = BASE_DIR / "main.pdf"
pdf_path = BASE_DIR / f"{output_name}.pdf"
icc_path = ICC_DIR / f"{icc_name}.icc"

print(f"[typst] compiling {MAIN_TYP} → {raw_pdf_path}")
result = subprocess.run(
    ["typst", "compile", str(MAIN_TYP), str(raw_pdf_path)],
    capture_output=True,
    text=True,
)
if result.returncode != 0:
    print(result.stderr)
    raise SystemExit("typst failed to compile")
print("[typst] done")

raw_info = pdf_info(raw_pdf_path)

gts_label = gts_raw or "Unknown"
print(f"[icc] using {icc_name} (mode: {mode}, GTS: {gts_label})")

with open(icc_path, "rb") as f:
    icc_data = f.read()

color_space_tag = icc_data[16:20].decode("ascii", errors="ignore")
channels = {"CMYK": 4, "RGB ": 3, "GRAY": 1}.get(color_space_tag, 3)

shutil.copy2(raw_pdf_path, pdf_path)

with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
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

print(f"[icc] applied → {pdf_path}")

out_info = pdf_info(pdf_path)
write_log(raw_pdf_path, pdf_path, raw_info, out_info)
