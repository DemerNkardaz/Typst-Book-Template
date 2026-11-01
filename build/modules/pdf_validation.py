import os
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree


class VeraPdfUnavailable(Exception):
    pass


class VeraPdfError(Exception):
    pass


VERAPDF_FLAVORS = {
    "PDF/A-1b": "1b",
    "PDF/A-1a": "1a",
    "PDF/A-2b": "2b",
    "PDF/A-2u": "2u",
    "PDF/A-2a": "2a",
    "PDF/A-3b": "3b",
    "PDF/A-3u": "3u",
    "PDF/A-3a": "3a",
    "PDF/A-4": "4",
    "PDF/A-4f": "4f",
    "PDF/A-4e": "4e",
    "PDF/UA-1": "ua1",
}


def validate_pdf(pdf_path: Path, standard: str) -> None:
    flavor = VERAPDF_FLAVORS.get(standard)
    if flavor is None:
        raise ValueError(f"Unsupported veraPDF standard: {standard}")

    executable = shutil.which("verapdf") or shutil.which("verapdf.bat")
    if executable is None:
        raise VeraPdfUnavailable

    command = [
        executable,
        "-f",
        flavor,
        "--format",
        "xml",
        str(pdf_path),
    ]
    if os.name == "nt" and Path(executable).suffix.lower() in {".bat", ".cmd"}:
        command = ["cmd", "/c", *command]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise VeraPdfError(result.stderr or result.stdout)

    try:
        report = ElementTree.fromstring(result.stdout)
    except ElementTree.ParseError as exc:
        raise VeraPdfError("veraPDF returned an invalid XML report") from exc

    validations = [
        element
        for element in report.iter()
        if element.tag.rsplit("}", 1)[-1] == "validationReport"
    ]
    if not validations:
        raise VeraPdfError("veraPDF returned no validation report")

    failed_rules = [
        rule
        for rule in report.iter()
        if rule.tag.rsplit("}", 1)[-1] == "rule"
        and rule.get("status") == "failed"
    ]
    if any(validation.get("isCompliant") != "true" for validation in validations):
        details = []
        for rule in failed_rules:
            description = next(
                (
                    child.text
                    for child in rule
                    if child.tag.rsplit("}", 1)[-1] == "description" and child.text
                ),
                "",
            )
            clause = rule.get("clause")
            details.append(f"{clause}: {description}" if clause else description)
        summary = "\n".join(detail for detail in details if detail)
        message = f"The final PDF is not compliant with {standard}"
        raise VeraPdfError(f"{message}\n{summary}" if summary else message)
