from datetime import datetime
from pathlib import Path

from modules.i18n import info


def write_log(
    log_path: Path,
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
        icc = info.get("OutputIntent")
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

    log_path.write_text(content + "\n", encoding="utf-8")
    info("info.log-written", path=log_path)
