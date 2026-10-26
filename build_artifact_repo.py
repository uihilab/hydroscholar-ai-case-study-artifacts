from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
from pathlib import Path


DEST = Path(__file__).resolve().parent
CASES = [
    ("CS-I_Willamette_River_14211720", Path(r"C:\Users\Varun\PhD-Materials\Softwares\hydroscholar-ai-advanced-v2-archive-files\archive\hydro_experiments\20260222_230416_willamette_river_14211720_corr")),
    ("CS-II_St_John_River_Random_Forest", Path(r"C:\Users\Varun\PhD-Materials\Softwares\hydroscholar-ai-advanced-version-2-archive\hydro_experiments\20260223_154300_usgs_streamflow_ml_predictor_done")),
    ("CS-III_Lake_Oroville_Satellite_Monitoring", Path(r"C:\Users\Varun\PhD-Materials\Softwares\hydroscholar-ai-advanced-version-2-archive\hydro_experiments\20260305_204400_reservoir_sentinel_monitoring_done")),
    ("CS-IV_Onion_Creek_LSTM_Rainfall_Runoff", Path(r"C:\Users\Varun\PhD-Materials\Softwares\hydroscholar-ai-advanced-version-2-archive\hydro_experiments\20260226_010616_onion_creek_flashiness_analysi_done")),
    ("CS-V_ERA5_Columbia_River_Basin", Path(r"C:\Users\Varun\PhD-Materials\Softwares\hydroscholar-ai-advanced-version-2-archive\hydro_experiments\20260306_090216_high_resolution_spatial_downsc_done")),
]
MAX_BYTES = 25 * 1024 * 1024
SKIP_DIRS = {".pytest_cache", "__pycache__", ".mypy_cache", ".venv", "venv", "node_modules", "site-packages", "temp", "tmp", "build", "dist"}
EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib", ".exe", ".pem", ".key", ".crt", ".aux", ".out", ".spl", ".typed"}
INCLUDED_EXTENSIONS = {
    ".py", ".sh", ".json", ".jsonl", ".csv", ".txt", ".md", ".log",
    ".png", ".jpg", ".jpeg", ".pdf", ".docx", ".xlsx", ".geojson",
    ".shp", ".shx", ".dbf", ".prj", ".cpg", ".tex", ".bib", ".qmd",
    ".xml", ".yaml", ".yml", ".rst", ".h5", ".pkl", ".nc", ".nc4",
    ".tif", ".tiff", ".jp2",
}
TEXT_EXTENSIONS = {
    ".py", ".sh", ".json", ".jsonl", ".csv", ".txt", ".md", ".log",
    ".geojson", ".prj", ".cpg", ".tex", ".bib", ".qmd", ".xml",
    ".yaml", ".yml", ".rst",
}
CDS_KEY_REGEX = re.compile(r"b46b071c-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_copy(path: Path) -> tuple[bool, str]:
    if path.name == "research_paper.log":
        return False, "LaTeX compilation log omitted from public release because it contains local build paths"
    suffix = path.suffix.lower()
    if suffix in EXCLUDE_EXTENSIONS:
        return False, "compiled bytecode, LaTeX build auxiliary, or credential file"
    if suffix not in INCLUDED_EXTENSIONS:
        return False, "non-artifact file type"
    if path.stat().st_size > MAX_BYTES:
        return False, "larger than 25 MiB; retain in local workspace / data repository"
    return True, ""


def copy_and_sanitize(source_file: Path, destination_file: Path) -> int:
    shutil.copy2(source_file, destination_file)
    if destination_file.suffix.lower() in TEXT_EXTENSIONS:
        try:
            raw_bytes = destination_file.read_bytes()
            text = raw_bytes.decode("utf-8")
            # Normalize CRLF/CR to LF to match .gitattributes (* text=auto eol=lf)
            norm_text = text.replace("\r\n", "\n").replace("\r", "\n")
            norm_text = CDS_KEY_REGEX.sub("<REDACTED_CDS_API_KEY>", norm_text)
            out_bytes = norm_text.encode("utf-8")
            if out_bytes != raw_bytes:
                destination_file.write_bytes(out_bytes)
        except UnicodeDecodeError:
            pass
    return destination_file.stat().st_size


def main() -> None:
    missing = [str(path) for _, path in CASES if not path.exists()]
    if missing:
        raise SystemExit("Case-study archive(s) not found: " + ", ".join(missing))
    (DEST / "experiments").mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    folder_rows: list[dict[str, object]] = []

    for case_name, experiment in CASES:
        out = DEST / "experiments" / case_name
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True, exist_ok=True)
        copied = 0
        excluded = 0
        copied_bytes = 0
        exclusions: list[str] = []
        for root, dirs, files in os.walk(experiment, topdown=True):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            root_path = Path(root)
            rel_root = root_path.relative_to(experiment)
            for name in sorted(files):
                source_file = root_path / name
                try:
                    include, reason = should_copy(source_file)
                    size = source_file.stat().st_size
                except OSError as exc:
                    include, reason, size = False, f"unreadable: {exc}", 0
                rel_file = (rel_root / name).as_posix()
                if not include:
                    excluded += 1
                    exclusions.append(f"{rel_file} ({size / (1024 * 1024):.2f} MiB): {reason}")
                    manifest.append({"experiment": case_name, "path": rel_file, "status": "excluded", "reason": reason, "bytes": size})
                    continue
                destination_file = out / rel_root / name
                destination_file.parent.mkdir(parents=True, exist_ok=True)
                try:
                    final_size = copy_and_sanitize(source_file, destination_file)
                    digest = sha256(destination_file)
                except OSError as exc:
                    excluded += 1
                    reason = f"copy failed: {exc}"
                    exclusions.append(f"{rel_file}: {reason}")
                    manifest.append({"experiment": case_name, "path": rel_file, "status": "excluded", "reason": reason, "bytes": size})
                    continue
                copied += 1
                copied_bytes += final_size
                manifest.append({"experiment": case_name, "path": rel_file, "status": "included", "bytes": final_size, "sha256": digest})
        readme = out / "ARCHIVE_README.md"
        lines = [
            f"# {case_name}",
            "",
            "This folder is a case-study artifact archive. It contains the experiment plan, provenance log, generated task scripts, tabular data products, model artifacts, sub-25 MiB NetCDF spatial grids, figures, and reports copied from the archived workflow workspace.",
            "",
            "It does not contain the HydroScholar AI application source code. Raw binary datasets larger than 25 MiB and LaTeX auxiliary build files were excluded; see `MANIFEST.csv` for their exact paths and sizes.",
            "",
            f"- Included files: {copied}",
            f"- Included size: {copied_bytes / (1024 * 1024):.2f} MiB",
            f"- Excluded files: {excluded}",
            "",
        ]
        if exclusions:
            lines += ["## Exclusions from this folder", "", "```text"] + exclusions[:100] + (["... additional exclusions recorded in `MANIFEST.csv` ..."] if len(exclusions) > 100 else []) + ["```", ""]
        readme.write_bytes(("\n".join(lines)).encode("utf-8"))
        folder_rows.append({"experiment": case_name, "source_archive_id": experiment.name, "included_files": copied, "included_bytes": copied_bytes, "excluded_files": excluded})

    with (DEST / "MANIFEST.csv").open("w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["experiment", "path", "status", "bytes", "sha256", "reason"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    with (DEST / "EXPERIMENT_INDEX.csv").open("w", newline="\n", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["experiment", "source_archive_id", "included_files", "included_bytes", "excluded_files"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(folder_rows)
    (DEST / "BUILD_METADATA.json").write_bytes(
        (json.dumps(
            {
                "case_studies": [{"name": name, "source_archive_id": path.name} for name, path in CASES],
                "case_study_count": len(folder_rows),
                "source_archive_identifier_note": "Original local filesystem paths are intentionally omitted from the public release.",
                "manifest_hash_basis": "SHA-256 of the exact included file bytes in the release working tree; text files are normalized to LF by .gitattributes.",
                "max_file_size_bytes": MAX_BYTES,
                "excluded_directories": sorted(SKIP_DIRS),
                "excluded_extensions": sorted(EXCLUDE_EXTENSIONS),
                "included_extensions": sorted(INCLUDED_EXTENSIONS),
            },
            indent=2,
        ) + "\n").encode("utf-8")
    )


if __name__ == "__main__":
    main()
