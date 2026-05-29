import io
import subprocess
import sys
import yaml
from pathlib import Path
import pikepdf
from pikepdf import Dictionary, Array, Name, Stream
from datetime import datetime
import shutil
import re

if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).parent
LAYOUT_YML = BASE_DIR / "settings" / "layout.yml"
BUILD_YML = BASE_DIR / "settings" / "build.yml"
BOOK_YML = BASE_DIR / "meta" / "book.yml"
PROPERTIES_YML = BASE_DIR / "meta" / "property.yml"
ICC_DIR = BASE_DIR / "assets" / "ICC"
MAIN_TYP = BASE_DIR / "main.typ"
LOG_PATH = BASE_DIR / "build.log"


def roman_to_int(s: str) -> int:
    roman_map = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000,
    }
    total = 0
    prev_value = 0
    for char in reversed(s.upper()):
        current_value = roman_map.get(char, 0)
        if current_value < prev_value:
            total -= current_value
        else:
            total += current_value
        prev_value = current_value
    return total


NS_PREFIXES = {
    "http://prismstandard.org/namespaces/basic/1.0/",
    "http://purl.org/dc/elements/1.1/",
    "http://ns.adobe.com/xap/1.0/",
    "http://ns.adobe.com/xap/1.0/rights/",
    "http://ns.adobe.com/photoshop/1.0/",
}


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

        xmp = pdf.open_metadata()
        part = xmp.get("pdfaid:part")
        conformance = xmp.get("pdfaid:conformance")
        if part and conformance:
            info["pdf_standard"] = f"PDF/A-{part}{conformance.lower()}"
        else:
            info["pdf_standard"] = None

        xmp_info: dict[str, object] = {}
        for key in xmp:
            uri = key.strip("{").split("}")[0]
            if uri in NS_PREFIXES:
                val = xmp.get(key)
                if val:
                    refinedKey = re.sub(r"\{([^}]+)\}", r"\1", key)
                    xmp_info[refinedKey] = str(val)
        info["xmp"] = xmp_info if xmp_info else None

        intents = pdf.Root.get("/OutputIntents")
        if intents:
            intent = intents[0]
            icc_info: dict[str, object] = {
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
    std: str | None = None,
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
            f"path:         {path}",
            f"size:         {fmt_size(info['size_bytes'])}",
            f"pages:        {info['pages']}",
            f"pdf version:  {info['pdf_version']}",
            f"pdf standard: {info.get('pdf_standard') or '—'}",
            f"title:        {info.get('Title') or '—'}",
            f"author:       {info.get('Author') or '—'}",
            f"creator:      {info.get('Creator') or '—'}",
            f"producer:     {info.get('Producer') or '—'}",
            f"created:      {info.get('CreationDate') or '—'}",
            f"modified:     {info.get('ModDate') or '—'}",
        ]
        icc = info["OutputIntent"]
        if isinstance(icc, dict):
            lines += [
                f"icc profile:  {icc.get('OutputConditionIdentifier')}",
                f"icc space:    {icc.get('color_space', '—')}",
                f"icc size:     {fmt_size(icc.get('size_bytes'))}",
            ]
        else:
            lines.append("icc profile:  not yet assigned")
        xmp = info.get("xmp")
        if isinstance(xmp, dict):
            lines.append("")
            for k, v in xmp.items():
                label = k.ljust(60)
                lines.append(f"{label} {v}")
        return "\n".join(lines)

    content = "\n\n".join([
        f"build log — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        section(raw_path, raw_info),
        section(out_path, out_info),
    ])

    LOG_PATH.write_text(content + "\n", encoding="utf-8")
    print(f"[log] {LOG_PATH}")


def convert_images(
    pdf: pikepdf.Pdf, icc_data: bytes, dst_channels: int
) -> int:
    from PIL import Image, ImageCms
    import io as _io

    dst_profile = ImageCms.ImageCmsProfile(_io.BytesIO(icc_data))
    dst_mode = "CMYK" if dst_channels == 4 else "RGB"

    converted = 0
    for page in pdf.pages:
        resources = page.get("/Resources")
        if not resources:
            continue
        xobjects = resources.get("/XObject")
        if not xobjects:
            continue
        for key in xobjects.keys():
            xobj = xobjects[key]
            if xobj.get("/Subtype") != "/Image":
                continue

            try:
                raw = bytes(xobj.read_bytes())
                width = int(xobj["/Width"])
                height = int(xobj["/Height"])
                cs = xobj.get("/ColorSpace")

                if (
                    isinstance(cs, pikepdf.Array)
                    and str(cs[0]) == "/ICCBased"
                ):
                    src_icc = bytes(cs[1].read_bytes())
                    src_profile = ImageCms.ImageCmsProfile(
                        _io.BytesIO(src_icc)
                    )
                else:
                    src_profile = ImageCms.createProfile("sRGB")

                img = Image.frombytes("RGB", (width, height), raw)
            except Exception as e:
                print(f"  skip {key}: {e}")
                continue

            img = img.convert("RGB")

            transform = ImageCms.buildTransform(
                src_profile,
                dst_profile,
                "RGB",
                dst_mode,
                renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
            )
            out_img = ImageCms.applyTransform(img, transform)
            if out_img is None:
                continue

            buf = _io.BytesIO()
            out_img.save(buf, format="JPEG", quality=95)
            new_data = buf.getvalue()

            xobj.write(new_data, filter=Name("/DCTDecode"))
            xobj["/ColorSpace"] = (
                Name("/DeviceCMYK")
                if dst_channels == 4
                else Name("/DeviceRGB")
            )
            if dst_channels == 4:
                xobj["/Decode"] = pikepdf.Array(
                    [1, 0, 1, 0, 1, 0, 1, 0]
                )
            converted += 1

    return converted


with open(LAYOUT_YML, encoding="utf-8") as f:
    layout = yaml.safe_load(f)

with open(BUILD_YML, encoding="utf-8") as f:
    build = yaml.safe_load(f)

with open(BOOK_YML, encoding="utf-8") as f:
    book = yaml.safe_load(f)

with open(PROPERTIES_YML, encoding="utf-8") as f:
    book_properties = yaml.safe_load(f)

mode = layout["mode"]
mode_config = build[f"mode-{mode}"]

output_name = build["output-file-name"]
icc_name = mode_config["ICC"]
pdf_standard_raw = mode_config.get("pdf-standard")
color_conversion = bool(build.get("color-conversion", False))

pdf_standard_to_standard = {
    "PDF 1.4":  "1.4",
    "PDF 1.5":  "1.5",
    "PDF 1.6":  "1.6",
    "PDF 1.7":  "1.7",
    "PDF 2.0":  "2.0",
    "PDF/A-1b": "a-1b",
    "PDF/A-1a": "a-1a",
    "PDF/A-2b": "a-2b",
    "PDF/A-2u": "a-2u",
    "PDF/A-2a": "a-2a",
    "PDF/A-3b": "a-3b",
    "PDF/A-3u": "a-3u",
    "PDF/A-3a": "a-3a",
    "PDF/A-4":  "a-4",
    "PDF/A-4f": "a-4f",
    "PDF/A-4e": "a-4e",
    "PDF/UA-1": "ua-1",
}

pdf_standard = pdf_standard_to_standard.get(pdf_standard_raw)

raw_pdf_path = BASE_DIR / "main.pdf"
pdf_path = BASE_DIR / f"{output_name} [{mode}].pdf"
icc_path = ICC_DIR / f"{icc_name}.icc"

print(f"[typst] compiling {MAIN_TYP} → {raw_pdf_path}")
typst_cmd = [
    "typst", "compile",
    str(MAIN_TYP), str(raw_pdf_path),
]

pages = mode_config.get("pages")
if pages is not None:
    typst_cmd += ["--pages", str(pages)]
if pdf_standard is not None:
    typst_cmd += ["--pdf-standard", pdf_standard]

result = subprocess.run(
    typst_cmd,
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print(result.stderr)
    raise SystemExit("typst failed to compile")
print("[typst] done")

raw_info = pdf_info(raw_pdf_path)

pdf_standard_label = pdf_standard_raw or "—"
print(f"[icc] using {icc_name} (mode: {mode}, standard: {pdf_standard_label})")

with open(icc_path, "rb") as f:
    icc_data = f.read()

color_space_tag = icc_data[16:20].decode("ascii", errors="ignore")
channels = {"CMYK": 4, "RGB ": 3, "GRAY": 1}.get(color_space_tag, 3)

shutil.copy2(raw_pdf_path, pdf_path)

with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
    if color_conversion:
        n = convert_images(pdf, icc_data, channels)
        print(f"[cc] images converted: {n}")

    icc_stream = Stream(pdf, icc_data)
    icc_stream["/N"] = channels

    output_intent = Dictionary(
        Type=Name("/OutputIntent"),
        OutputConditionIdentifier=pikepdf.String(icc_name),
        DestOutputProfile=icc_stream,
    )

    pdf.Root["/OutputIntents"] = Array([pdf.make_indirect(output_intent)])
    with pdf.open_metadata() as meta:
        def m(key: str, val: object) -> None:
            if val is not None:
                meta[key] = str(val)

        m("prism:title",               book.get("title"))
        m("prism:subtitle",            book.get("sub-title"))
        m("prism:section",             book.get("section"))
        m("prism:teaser",              book.get("teaser"))
        m("prism:category",            book.get("genre"))
        m("prism:isPartOf",            book.get("cycle"))
        m("prism:seriesTitle",         book.get("series"))
        m("prism:issueName",           book.get("volume-title"))
        m("prism:volume",              (
            roman_to_int(book["volume"])
            if book.get("volume")
            else None
        ))
        m("prism:url",                 book.get("publication-url"))
        m("prism:isbn",                book_properties.get("ISBN"))
        m("prism:issn",                book_properties.get("ISSN"))
        m("prism:doi",                 book_properties.get("DOI"))
        m("dc:rights",                 book.get("copyright-notice"))
        m("prism:copyright",           book.get("copyright-notice"))
        m("xmpRights:WebStatement",    book.get("author-url"))
        m("xmpRights:Marked",          (
            "True" if book.get("copyright") else None
        ))
        m("xmp:Nickname",              book.get("title-short"))
        m("photoshop:AuthorsPosition", book.get("author-position"))
        m("photoshop:CaptionWriter",   book.get("description-author"))

    pdf.save(pdf_path)

print(f"[icc] applied → {pdf_path}")

if build.get("open-after-build", False):
    CREATE_BREAKAWAY_FROM_JOB = 0x01000000
    subprocess.Popen(
        ["cmd", "/c", "start", "", str(pdf_path)],
        shell=False,
        creationflags=subprocess.DETACHED_PROCESS | CREATE_BREAKAWAY_FROM_JOB,
    )

out_info = pdf_info(pdf_path)
write_log(raw_pdf_path, pdf_path, raw_info, out_info, std=pdf_standard_raw)
