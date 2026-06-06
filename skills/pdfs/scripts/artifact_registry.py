#!/usr/bin/env python3
"""Register and inspect local PDF/DOCX output artifacts.

The registry is a lightweight JSONL file under ``outputs/artifacts``.  It
records metadata for files that already exist under the local workbench's
``outputs/`` directory.  It deliberately does not generate download links,
serve files, or emulate ChatGPT's hosted artifact UI.

Examples:
  python artifact_registry.py register outputs/final.pdf \
    --type application/pdf \
    --description "Final PDF" \
    --producer "pdf_edit.py merge"
  python artifact_registry.py list
  python artifact_registry.py show final-<hash12>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_REGISTRY_REL = "outputs/artifacts/registry.jsonl"
RECORD_FIELDS = [
    "artifact_id",
    "path",
    "type",
    "description",
    "sha256",
    "size_bytes",
    "producer",
    "created_at",
    "preview_path",
    "preview_note",
]
TEXT_FIELDS = {"artifact_id", "path", "type", "description", "sha256", "producer", "created_at"}
OPTIONAL_TEXT_FIELDS = {"preview_path", "preview_note"}
ARTIFACT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class RegistryError(Exception):
    """Raised for user-correctable registry errors."""


def repo_root() -> Path:
    """Return the repository root for this skill package."""

    # repo/skills/pdfs/scripts/artifact_registry.py -> repo
    return Path(__file__).resolve().parents[3]


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_user_path(raw_path: str, root: Path) -> Path:
    """Resolve a user path as absolute or repo-relative.

    Relative paths are interpreted from the repository root, not the process
    current directory.  This keeps recorded paths deterministic when the script
    is invoked from another working directory.
    """

    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve(strict=False)


def require_inside_repo(path: Path, root: Path, label: str) -> None:
    if not is_relative_to(path, root):
        raise RegistryError(f"{label} must be inside the repository root")


def require_under_outputs(path: Path, root: Path, label: str) -> None:
    outputs_root = (root / "outputs").resolve(strict=False)
    require_inside_repo(path, root, label)
    if not is_relative_to(path, outputs_root):
        raise RegistryError(f"{label} must be under outputs/")


def repo_relative_posix(path: Path, root: Path) -> str:
    require_inside_repo(path, root, "path")
    return path.relative_to(root).as_posix()


def resolve_registry_path(raw_path: str, root: Path) -> Path:
    registry_path = resolve_user_path(raw_path, root)
    require_under_outputs(registry_path, root, "registry path")
    if registry_path.exists() and registry_path.is_dir():
        raise RegistryError("registry path must be a file, not a directory")
    return registry_path


def resolve_existing_output_file(raw_path: str, root: Path, label: str) -> Path:
    path = resolve_user_path(raw_path, root)
    require_under_outputs(path, root, label)
    if not path.is_file():
        raise RegistryError(f"{label} does not exist or is not a file")
    return path


def clean_text(value: Optional[str], field_name: str, *, required: bool = False) -> Optional[str]:
    if value is None:
        if required:
            raise RegistryError(f"{field_name} is required")
        return None
    cleaned = value.strip()
    if required and not cleaned:
        raise RegistryError(f"{field_name} must not be empty")
    if "\x00" in cleaned:
        raise RegistryError(f"{field_name} must not contain NUL bytes")
    return cleaned


def validate_artifact_id(artifact_id: str) -> str:
    cleaned = clean_text(artifact_id, "artifact ID", required=True)
    assert cleaned is not None
    if not ARTIFACT_ID_RE.fullmatch(cleaned):
        raise RegistryError(
            "artifact ID must start with a letter or number and contain only "
            "letters, numbers, dots, underscores, or hyphens (max 128 chars)"
        )
    return cleaned


def sanitize_stem(stem: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", stem.lower()).strip(".-_")
    if not safe:
        safe = "artifact"
    return safe[:80]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_stored_output_path(value: str, line_no: int, field_name: str) -> None:
    if not value:
        raise RegistryError(f"malformed registry row {line_no}: {field_name} must not be empty")
    if "\\" in value:
        raise RegistryError(f"malformed registry row {line_no}: {field_name} must use POSIX separators")
    if re.match(r"^[A-Za-z]:/", value) or value.startswith("//"):
        raise RegistryError(f"malformed registry row {line_no}: {field_name} must be repo-relative")
    posix_path = PurePosixPath(value)
    if posix_path.is_absolute() or ".." in posix_path.parts:
        raise RegistryError(f"malformed registry row {line_no}: {field_name} must be repo-relative")
    if not posix_path.parts or posix_path.parts[0] != "outputs":
        raise RegistryError(f"malformed registry row {line_no}: {field_name} must be under outputs/")


def validate_record(record: Any, line_no: int) -> Dict[str, Any]:
    if not isinstance(record, dict):
        raise RegistryError(f"malformed registry row {line_no}: row is not a JSON object")
    missing = [field for field in RECORD_FIELDS if field not in record]
    if missing:
        raise RegistryError(
            f"malformed registry row {line_no}: missing field(s): {', '.join(missing)}"
        )
    unknown = [field for field in record if field not in RECORD_FIELDS]
    if unknown:
        raise RegistryError(
            f"malformed registry row {line_no}: unexpected field(s): {', '.join(unknown)}"
        )
    for field in TEXT_FIELDS:
        if not isinstance(record[field], str):
            raise RegistryError(f"malformed registry row {line_no}: {field} must be a string")
    for field in OPTIONAL_TEXT_FIELDS:
        if record[field] is not None and not isinstance(record[field], str):
            raise RegistryError(
                f"malformed registry row {line_no}: {field} must be a string or null"
            )
    if not isinstance(record["size_bytes"], int) or record["size_bytes"] < 0:
        raise RegistryError(f"malformed registry row {line_no}: size_bytes must be a non-negative integer")
    if not ARTIFACT_ID_RE.fullmatch(record["artifact_id"]):
        raise RegistryError(f"malformed registry row {line_no}: artifact_id is invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
        raise RegistryError(f"malformed registry row {line_no}: sha256 must be 64 lowercase hex characters")
    validate_stored_output_path(record["path"], line_no, "path")
    if record["preview_path"] is not None:
        validate_stored_output_path(record["preview_path"], line_no, "preview_path")
    return record


def load_records(registry_path: Path) -> List[Dict[str, Any]]:
    if not registry_path.exists():
        return []
    records: List[Dict[str, Any]] = []
    with registry_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise RegistryError(f"malformed registry row {line_no}: {exc.msg}") from exc
            records.append(validate_record(record, line_no))
    return records


def append_record(registry_path: Path, record: Dict[str, Any]) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with registry_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=False))
        handle.write("\n")


def persistent_items(record: Dict[str, Any], *, include_id: bool = True) -> Tuple[Tuple[str, Any], ...]:
    ignored = {"created_at"}
    if not include_id:
        ignored.add("artifact_id")
    return tuple((field, record[field]) for field in RECORD_FIELDS if field not in ignored)


def build_record(args: argparse.Namespace, root: Path) -> Dict[str, Any]:
    artifact_path = resolve_existing_output_file(args.artifact_path, root, "artifact path")
    preview_path: Optional[Path] = None
    if args.preview:
        preview_path = resolve_existing_output_file(args.preview, root, "preview path")

    file_hash = sha256_file(artifact_path)
    artifact_id = validate_artifact_id(args.artifact_id) if args.artifact_id else f"{sanitize_stem(artifact_path.stem)}-{file_hash[:12]}"

    artifact_type = clean_text(args.artifact_type, "type", required=True)
    description = clean_text(args.description, "description", required=True)
    producer = clean_text(args.producer, "producer") or ""
    preview_note = clean_text(args.preview_note, "preview note")

    assert artifact_type is not None
    assert description is not None

    return {
        "artifact_id": artifact_id,
        "path": repo_relative_posix(artifact_path, root),
        "type": artifact_type,
        "description": description,
        "sha256": file_hash,
        "size_bytes": artifact_path.stat().st_size,
        "producer": producer,
        "created_at": utc_timestamp(),
        "preview_path": repo_relative_posix(preview_path, root) if preview_path else None,
        "preview_note": preview_note,
    }


def register_record(registry_path: Path, candidate: Dict[str, Any]) -> Dict[str, Any]:
    records = load_records(registry_path)

    for existing in records:
        if existing["artifact_id"] == candidate["artifact_id"]:
            if persistent_items(existing) == persistent_items(candidate):
                return existing
            raise RegistryError(
                "artifact ID already exists with different metadata or content; "
                "update mode is not supported"
            )

    for existing in records:
        same_path_and_hash = existing["path"] == candidate["path"] and existing["sha256"] == candidate["sha256"]
        if same_path_and_hash and persistent_items(existing, include_id=False) == persistent_items(candidate, include_id=False):
            return existing
        if same_path_and_hash:
            raise RegistryError(
                "artifact path and content are already registered with different metadata; "
                "update mode is not supported"
            )

    append_record(registry_path, candidate)
    return candidate


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def print_record(record: Dict[str, Any]) -> None:
    for field in RECORD_FIELDS:
        value = record[field]
        print(f"{field}: {'' if value is None else value}")


def print_table(records: Iterable[Dict[str, Any]]) -> None:
    rows = [
        [
            record["artifact_id"],
            record["type"],
            str(record["size_bytes"]),
            record["path"],
            record["description"],
        ]
        for record in records
    ]
    if not rows:
        print("No artifacts registered.")
        return

    headers = ["artifact_id", "type", "size_bytes", "path", "description"]
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    print("  ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        print("  ".join(row[i].ljust(widths[i]) for i in range(len(headers))))


def cmd_register(args: argparse.Namespace) -> int:
    root = repo_root()
    registry_path = resolve_registry_path(args.registry, root)
    record = build_record(args, root)
    registered = register_record(registry_path, record)
    if args.json:
        print_json(registered)
    else:
        print_record(registered)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = repo_root()
    registry_path = resolve_registry_path(args.registry, root)
    records = load_records(registry_path)
    if args.json:
        print_json(records)
    else:
        print_table(records)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    root = repo_root()
    registry_path = resolve_registry_path(args.registry, root)
    artifact_id = validate_artifact_id(args.artifact_id)
    records = load_records(registry_path)
    for record in records:
        if record["artifact_id"] == artifact_id:
            if args.json:
                print_json(record)
            else:
                print_record(record)
            return 0
    raise RegistryError("artifact ID not found")


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--registry",
        default=DEFAULT_REGISTRY_REL,
        help=f"Registry JSONL path under outputs/ (default: {DEFAULT_REGISTRY_REL})",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Register and inspect local output artifacts")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_register = sub.add_parser("register", help="register an existing file under outputs/")
    add_common_flags(p_register)
    p_register.add_argument("artifact_path", help="Existing artifact file path under outputs/")
    p_register.add_argument("--type", dest="artifact_type", required=True, help="MIME-like artifact type")
    p_register.add_argument("--description", required=True, help="Human-readable artifact description")
    p_register.add_argument("--producer", default="", help="Producer command or note")
    p_register.add_argument("--id", dest="artifact_id", help="Explicit artifact ID")
    p_register.add_argument("--preview", help="Optional existing preview file path under outputs/")
    p_register.add_argument("--preview-note", help="Optional preview note")
    p_register.set_defaults(func=cmd_register)

    p_list = sub.add_parser("list", help="list registered artifacts")
    add_common_flags(p_list)
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="show one registered artifact by ID")
    add_common_flags(p_show)
    p_show.add_argument("artifact_id", help="Artifact ID to inspect")
    p_show.set_defaults(func=cmd_show)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RegistryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
