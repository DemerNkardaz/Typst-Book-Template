import os
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree


class VeraPdfUnavailable(Exception):
    pass


class VeraPdfError(Exception):
    pass


def validate_pdf_ua(pdf_path: Path) -> None:
    executable = shutil.which("verapdf") or shutil.which("verapdf.bat")
    if executable is None:
        raise VeraPdfUnavailable

    command = [
        executable,
        "-f",
        "ua1",
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
        message = "The final PDF is not compliant with PDF/UA-1"
        raise VeraPdfError(f"{message}\n{summary}" if summary else message)
