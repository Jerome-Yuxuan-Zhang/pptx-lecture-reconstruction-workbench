from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

from app.config import AppConfig
from app.models.task_models import TaskRecord
from app.services.export_service import ExportService
from app.services.qa_service import QAService
from app.utils.file_utils import dump_json, ensure_directory


class TaskService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.export_service = ExportService(config)
        self.qa_service = QAService()
        self.tasks_dir = ensure_directory(config.output_dir / "tasks")

    def create_task(self, kind: str, input_path: Path) -> TaskRecord:
        task = TaskRecord(
            task_id=uuid.uuid4().hex, kind=kind, input_path=input_path, status="pending"
        )
        self._persist(task)
        return task

    def get_task(self, task_id: str) -> TaskRecord:
        path = self.tasks_dir / f"{task_id}.json"
        return TaskRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def run_ppt_to_docx(self, input_path: Path, output_path: Path | None = None) -> TaskRecord:
        task = self.create_task("ppt-to-docx", input_path)
        task.status = "running"
        self._persist(task)
        artifact_root = ensure_directory(
            (output_path.parent / input_path.stem)
            if output_path is not None
            else (self.config.output_dir / input_path.stem)
        )
        try:
            document_ir, root = self.export_service.parse_pptx(input_path, artifact_root)
            self.export_service.export_ir(document_ir, root)
            task.output_path = self.export_service.export_docx(
                document_ir,
                output_path or root / f"{input_path.stem}.docx",
            )
            _, qa_md = self.qa_service.build_report(document_ir, root)
            task.report_path = qa_md
            task.status = "completed"
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.error_message = str(exc)
        task.updated_at = datetime.now(UTC)
        self._persist(task)
        return task

    def _persist(self, task: TaskRecord) -> Path:
        task.updated_at = datetime.now(UTC)
        return dump_json(self.tasks_dir / f"{task.task_id}.json", task.model_dump(mode="json"))
