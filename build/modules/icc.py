import re
from pathlib import Path

import pikepdf
from pikepdf import Array, Dictionary, Name, Stream

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
                    refined_key = re.sub(r"\{([^}]+)\}", r"\1", key)
                    xmp_info[refined_key] = str(val)
        info["xmp"] = xmp_info if xmp_info else None

        intents = pdf.Root.get("/OutputIntents")
        if intents:
            intent = intents[0]
            icc_info: dict[str, object] = {
                "OutputConditionIdentifier": str(intent.get("/OutputConditionIdentifier")),
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


def get_color_channels(icc_data: bytes) -> int:
    color_space_tag = icc_data[16:20].decode("ascii", errors="ignore")
    return {"CMYK": 4, "RGB ": 3, "GRAY": 1}.get(color_space_tag, 3)


def apply_output_intent(
    pdf: pikepdf.Pdf,
    icc_data: bytes,
    channels: int,
    icc_name: str,
) -> None:
    icc_stream = Stream(pdf, icc_data)
    icc_stream["/N"] = channels

    output_intent = Dictionary(
        Type=Name("/OutputIntent"),
        OutputConditionIdentifier=pikepdf.String(icc_name),
        DestOutputProfile=icc_stream,
    )

    pdf.Root["/OutputIntents"] = Array([pdf.make_indirect(output_intent)])
