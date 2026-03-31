from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def derive_output_path(input_path: Path, output_path: Path | None, suffix: str) -> Path:
    if output_path:
        ensure_directory(output_path.parent)
        return output_path
    return input_path.with_suffix(suffix)


def make_task_dir(root: Path, prefix: str = "task") -> Path:
    task_dir = root / f"{prefix}-{uuid.uuid4().hex[:8]}"
    task_dir.mkdir(parents=True, exist_ok=True)
    return task_dir


def dump_json(path: Path, data: Any) -> Path:
    ensure_directory(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path
