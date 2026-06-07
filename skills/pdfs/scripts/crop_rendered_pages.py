#!/usr/bin/env python3
"""Create focused QA crops from rendered PDF page images.

Use this after rendering final PDF pages with render_pdf.py. The crop spec
records exactly which local regions were inspected and what each crop verifies.

Example:
  python crop_rendered_pages.py outputs/task/focused-crops.json --base_dir . --json
  python crop_rendered_pages.py outputs/task/focused-crops.json --dry_run --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from PIL import Image


Box = Tuple[int, int, int, int]


def _read_spec(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in crop spec {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Crop spec root must be a JSON object")
    crops = data.get("crops")
    if not isinstance(crops, list) or not crops:
        raise ValueError("Crop spec must contain a non-empty 'crops' list")
    return data


def _resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return base_dir / path


def _parse_box(value: Any) -> Box:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("Crop box must be a four-item array")
    if len(value) != 4:
        raise ValueError("Crop box must contain exactly four values: [left, top, right, bottom]")
    try:
        left, top, right, bottom = (int(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Crop box values must be integers") from exc
    if right <= left or bottom <= top:
        raise ValueError(f"Invalid crop box with non-positive size: {list(value)}")
    return left, top, right, bottom


def _validate_box_within_image(box: Box, image_size: Tuple[int, int], name: str) -> None:
    left, top, right, bottom = box
    width, height = image_size
    if left < 0 or top < 0 or right > width or bottom > height:
        raise ValueError(
            f"Crop '{name}' box {list(box)} is outside source image bounds "
            f"{width}x{height}"
        )


def _parse_string_list(value: Any, field: str, name: str, strict: bool) -> List[str]:
    if value is None:
        if strict:
            raise ValueError(f"Crop '{name}' must include a non-empty '{field}' list in strict mode")
        return []
    if not isinstance(value, list) or not value:
        raise ValueError(f"Crop '{name}' field '{field}' must be a non-empty string list")

    items: List[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"Crop '{name}' field '{field}' item {index} must be a non-empty string"
            )
        items.append(item.strip())
    return items


def _crop_record(
    record: Dict[str, Any],
    base_dir: Path,
    dry_run: bool,
    strict: bool,
) -> Dict[str, Any]:
    name = str(record.get("name") or "")
    if not name:
        raise ValueError("Each crop must include a non-empty 'name'")

    source_value = record.get("source")
    output_value = record.get("output")
    verifies = str(record.get("verifies") or "")
    if not isinstance(source_value, str) or not source_value:
        raise ValueError(f"Crop '{name}' must include a non-empty 'source' path")
    if not isinstance(output_value, str) or not output_value:
        raise ValueError(f"Crop '{name}' must include a non-empty 'output' path")
    if not verifies:
        raise ValueError(f"Crop '{name}' must include a non-empty 'verifies' note")
    checks = _parse_string_list(record.get("checks"), "checks", name, strict)
    reject_if = _parse_string_list(record.get("reject_if"), "reject_if", name, strict)

    source = _resolve_path(source_value, base_dir)
    output = _resolve_path(output_value, base_dir)
    if not source.exists():
        raise FileNotFoundError(f"Crop '{name}' source image not found: {source}")

    box = _parse_box(record.get("box"))
    with Image.open(source) as image:
        image_size = (image.width, image.height)
        _validate_box_within_image(box, image_size, name)
        crop_size = (box[2] - box[0], box[3] - box[1])
        if not dry_run:
            output.parent.mkdir(parents=True, exist_ok=True)
            image.crop(box).save(output)

    summary: Dict[str, Any] = {
        "name": name,
        "source": source_value,
        "output": output_value,
        "box": list(box),
        "verifies": verifies,
        "checks": checks,
        "reject_if": reject_if,
        "source_size": list(image_size),
        "output_size": list(crop_size),
    }
    if dry_run:
        summary["dry_run"] = True
    return summary


def crop_from_spec(spec_path: Path, base_dir: Path, dry_run: bool, strict: bool) -> Dict[str, Any]:
    spec = _read_spec(spec_path)
    crops: List[Dict[str, Any]] = []
    for raw_record in spec["crops"]:
        if not isinstance(raw_record, dict):
            raise ValueError("Each crop entry must be a JSON object")
        crops.append(_crop_record(raw_record, base_dir, dry_run=dry_run, strict=strict))

    return {
        "spec": str(spec_path),
        "base_dir": str(base_dir),
        "task": spec.get("task"),
        "dry_run": dry_run,
        "strict": strict,
        "crop_count": len(crops),
        "crops": crops,
    }


def _print_text_summary(summary: Dict[str, Any]) -> None:
    mode = "validated" if summary["dry_run"] else "written"
    print(f"{mode} {summary['crop_count']} crop(s)")
    for crop in summary["crops"]:
        print(f"- {crop['output']}: {crop['verifies']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create focused QA crops from rendered PDF pages")
    parser.add_argument("spec", help="JSON crop specification")
    parser.add_argument(
        "--base_dir",
        default=".",
        help="Base directory for relative paths in the spec (default: current directory)",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Validate the spec and report crop sizes without writing images",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require each crop to include non-empty checks and reject_if lists",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON summary")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = base_dir / spec_path
    summary = crop_from_spec(spec_path, base_dir, dry_run=args.dry_run, strict=args.strict)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        _print_text_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
