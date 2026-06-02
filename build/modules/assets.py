from pathlib import Path
import tempfile
import urllib.request
import zipfile
import yaml

from modules.i18n import info, succes

BASE_DIR = Path(__file__).resolve().parents[2]
REGISTRY_YML = BASE_DIR / "assets" / "registry.yml"
ASSET_EXTENSIONS = {".icc", ".icm"}


def download_file(url: str, target: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(target, "wb") as dst:
        dst.write(resp.read())


def fetch_assets() -> None:
    with open(REGISTRY_YML, encoding="utf-8") as f:
        register = yaml.safe_load(f)

    for folder_name, entries in register.items():
        folder_path = BASE_DIR / "assets" / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        for asset_name, url in entries.items():
            existing = next(folder_path.glob(f"{asset_name}.*"), None)
            if existing:
                succes("info.assets-found", folder=folder_name, name=existing.name)
                continue

            info(
                "info.assets-downloading",
                folder=folder_name,
                name=asset_name,
                url=url,
            )
            is_zip = url.lower().endswith(".zip")

            if is_zip:
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                download_file(url, tmp_path)
                with zipfile.ZipFile(tmp_path) as zf:
                    for member in zf.namelist():
                        member_path = Path(member)
                        if member_path.suffix.lower() in ASSET_EXTENSIONS:
                            target = folder_path / f"{asset_name}{member_path.suffix}"
                            with zf.open(member) as src, open(target, "wb") as dst:
                                dst.write(src.read())
                            info("info.assets-extracted", name=target.name)
                tmp_path.unlink()
            else:
                suffix = Path(url).suffix
                target = folder_path / f"{asset_name}{suffix}"
                download_file(url, target)
                info("info.assets-saved", name=target.name)
