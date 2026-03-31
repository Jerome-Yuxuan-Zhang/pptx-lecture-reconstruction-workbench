from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["pending", "running", "completed", "failed"]


class TaskRecord(BaseModel):
    task_id: str
    status: TaskStatus = "pending"
    kind: str
    input_path: Path
    output_path: Path | None = None
    report_path: Path | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
