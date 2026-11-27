"""Bounded extraction of the licensed TrafficSigns-Raw subtree from a verified ZIP.

The caller is responsible for verifying the archive SHA-256 before extraction.
Only the TrafficSigns-Raw directory and its dataset-specific license notice
are extracted. ZIP paths, entry types, file counts and expanded sizes are bounded.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import zipfile
from pathlib import Path, PurePosixPath

DEFAULT_MAX_TOTAL_BYTES = 1_000_000_000
DEFAULT_MAX_FILE_BYTES = 100_000_000
DEFAULT_MAX_FILES = 20_000
CHUNK_SIZE = 1024 * 1024


def _validated_member_name(name: str) -> tuple[str, bool]:
    """Return a normalized POSIX member path and directory flag."""
    if not isinstance(name, str) or not name or "\x00" in name:
        raise ValueError("ZIP-Eintrag hat einen leeren oder ungültigen Pfad.")
    if "\\" in name:
        raise ValueError(f"ZIP-Pfad enthält einen Backslash: {name!r}")
    if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        raise ValueError(f"Absoluter ZIP-Pfad ist nicht erlaubt: {name!r}")

    is_directory = name.endswith("/")
    normalized = name[:-1] if is_directory else name
    parts = normalized.split("/")
    if not normalized or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Unsicherer ZIP-Pfad: {name!r}")
    path = PurePosixPath(normalized)
    if path.is_absolute():
        raise ValueError(f"Absoluter ZIP-Pfad ist nicht erlaubt: {name!r}")
    return path.as_posix(), is_directory


def extract_traffic_signs_raw(
    archive_path: Path,
    destination: Path,
    *,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_files: int = DEFAULT_MAX_FILES,
) -> dict:
    """Extract only TrafficSigns-Raw and its license notice under strict limits."""
    if type(max_total_bytes) is not int or max_total_bytes <= 0:
        raise ValueError("max_total_bytes muss eine positive Ganzzahl sein.")
    if type(max_file_bytes) is not int or max_file_bytes <= 0:
        raise ValueError("max_file_bytes muss eine positive Ganzzahl sein.")
    if type(max_files) is not int or max_files <= 0:
        raise ValueError("max_files muss eine positive Ganzzahl sein.")

    archive_path = Path(archive_path)
    destination = Path(destination)
    if not archive_path.is_file():
        raise FileNotFoundError(f"ZIP-Archiv fehlt: {archive_path}")
    if destination.exists():
        raise FileExistsError(f"Zielordner muss neu sein: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    extracted_total = 0
    extracted_files = 0

    try:
        with zipfile.ZipFile(archive_path) as source:
            names = [info.filename for info in source.infolist()]
            readmes = [
                name for name in names
                if name.endswith("/traffic_signs_raw/README.md")
            ]
            licenses = [
                name for name in names
                if name.endswith("/LICENSES/traffic_signs_license.txt")
            ]
            if len(readmes) != 1 or len(licenses) != 1:
                raise ValueError(
                    "TrafficSigns-Raw-README oder eindeutige Lizenzdatei fehlt."
                )

            raw_prefix = readmes[0][:-len("README.md")]
            license_path = licenses[0]
            selected = [
                info for info in source.infolist()
                if info.filename.startswith(raw_prefix) or info.filename == license_path
            ]
            if not selected:
                raise ValueError("Keine freizugebenden ZIP-Einträge gefunden.")

            seen_paths: set[str] = set()
            planned_files = 0
            planned_total = 0
            for info in selected:
                normalized, is_directory = _validated_member_name(info.filename)
                if normalized in seen_paths:
                    raise ValueError(f"Doppelter ZIP-Pfad: {normalized}")
                seen_paths.add(normalized)

                mode = (info.external_attr >> 16) & 0xFFFF
                file_type = stat.S_IFMT(mode)
                if stat.S_ISLNK(mode):
                    raise ValueError(f"Symbolischer Link im ZIP ist nicht erlaubt: {normalized}")
                if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ValueError(f"Spezieller Dateityp im ZIP ist nicht erlaubt: {normalized}")
                if is_directory:
                    if info.file_size != 0:
                        raise ValueError(f"ZIP-Verzeichnis enthält unerwartete Daten: {normalized}")
                    continue
                if file_type == stat.S_IFDIR:
                    raise ValueError(f"Dateieintrag ist als Verzeichnis markiert: {normalized}")
                if info.flag_bits & 0x1:
                    raise ValueError(f"Verschlüsselter ZIP-Eintrag wird nicht unterstützt: {normalized}")
                if info.file_size < 0 or info.file_size > max_file_bytes:
                    raise ValueError(f"ZIP-Datei überschreitet das Einzeldateilimit: {normalized}")

                planned_files += 1
                planned_total += info.file_size
                if planned_files > max_files:
                    raise ValueError("ZIP-Auswahl überschreitet das Dateianzahl-Limit.")
                if planned_total > max_total_bytes:
                    raise ValueError("ZIP-Auswahl überschreitet das entpackte Gesamtgrößenlimit.")

            if readmes[0] not in seen_paths or license_path not in seen_paths:
                raise ValueError("README oder Lizenzdatei fehlt in der Extraktionsauswahl.")

            for info in selected:
                normalized, is_directory = _validated_member_name(info.filename)
                target = root.joinpath(*PurePosixPath(normalized).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                resolved_target = target.resolve()
                if resolved_target != root and root not in resolved_target.parents:
                    raise ValueError(f"ZIP-Ziel liegt außerhalb des Extraktionsordners: {normalized}")

                if is_directory:
                    target.mkdir(exist_ok=True)
                    continue

                written = 0
                with source.open(info, "r") as source_file, target.open("xb") as target_file:
                    while True:
                        chunk = source_file.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        written += len(chunk)
                        extracted_total += len(chunk)
                        if written > max_file_bytes or extracted_total > max_total_bytes:
                            raise ValueError("Tatsächlich entpackte Daten überschreiten das Größenlimit.")
                        target_file.write(chunk)
                if written != info.file_size:
                    raise ValueError(f"Entpackte Dateigröße stimmt nicht: {normalized}")
                extracted_files += 1

        (destination / "traffic_signs_raw_source_path.txt").write_text(
            raw_prefix, encoding="utf-8"
        )
        (destination / "traffic_signs_raw_license_path.txt").write_text(
            license_path, encoding="utf-8"
        )
        return {
            "source_path": raw_prefix,
            "license_path": license_path,
            "files_extracted": extracted_files,
            "bytes_extracted": extracted_total,
            "max_total_bytes": max_total_bytes,
            "max_file_bytes": max_file_bytes,
            "max_files": max_files,
        }
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES)
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    args = parser.parse_args()
    report = extract_traffic_signs_raw(
        args.archive,
        args.destination,
        max_total_bytes=args.max_total_bytes,
        max_file_bytes=args.max_file_bytes,
        max_files=args.max_files,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
