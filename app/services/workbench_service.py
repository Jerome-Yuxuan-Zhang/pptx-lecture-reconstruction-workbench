from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.config import AppConfig
from app.services.export_service import ExportService
from app.services.llm_service import LLMService
from app.services.qa_service import QAService
from app.utils.file_utils import ensure_directory

StatusCallback = Callable[[str], None]


@dataclass(slots=True)
class WorkbenchOptions:
    export_docx: bool = True
    export_html: bool = True
    init_lossless_workfile: bool = True
    init_lecture_workfile: bool = True


@dataclass(slots=True)
class WorkbenchResult:
    artifact_root: Path
    asset_dir: Path
    ir_path: Path
    qa_json_path: Path
    qa_md_path: Path
    docx_path: Path | None = None
    html_path: Path | None = None
    lossless_workfile_path: Path | None = None
    lecture_workfile_path: Path | None = None
    html_note: str | None = None

    def existing_paths(self) -> list[Path]:
        ordered = [
            self.docx_path,
            self.html_path,
            self.ir_path,
            self.qa_md_path,
            self.qa_json_path,
            self.lossless_workfile_path,
            self.lecture_workfile_path,
            self.asset_dir,
            self.artifact_root,
        ]
        return [path for path in ordered if path and path.exists()]


class WorkbenchService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.export_service = ExportService(config)
        self.qa_service = QAService()
        self.llm_service = LLMService(config)

    def build_bundle(
        self,
        input_path: Path,
        output_dir: Path,
        options: WorkbenchOptions | None = None,
        on_status: StatusCallback | None = None,
    ) -> WorkbenchResult:
        options = options or WorkbenchOptions()
        output_dir = ensure_directory(output_dir)
        artifact_root = ensure_directory(output_dir / input_path.stem)
        self._report(on_status, f"Loading {input_path.name}")
        document_ir, _ = self.export_service.parse_pptx(input_path, artifact_root)

        self._report(on_status, "Writing IR")
        ir_path = self.export_service.export_ir(document_ir, artifact_root)

        self._report(on_status, "Building QA report")
        qa_json_path, qa_md_path = self.qa_service.build_report(document_ir, artifact_root)

        docx_path: Path | None = None
        if options.export_docx:
            self._report(on_status, "Exporting DOCX")
            docx_path = self.export_service.export_docx(
                document_ir,
                output_dir / f"{input_path.stem}.docx",
            )

        html_path: Path | None = None
        html_note: str | None = None
        if options.export_html:
            self._report(on_status, "Generating offline HTML draft")
            html, html_note = self.llm_service.generate_lecture_html(document_ir, use_llm=False)
            html_path = output_dir / f"{input_path.stem}.html"
            html_path.write_text(html, encoding="utf-8")

        lossless_workfile_path: Path | None = None
        if options.init_lossless_workfile:
            self._report(on_status, "Preparing lossless Codex workfile")
            lossless_workfile_path = self._copy_template(
                source=Path("docs/lossless_course_material_compiler_spec.md"),
                destination=output_dir / f"{input_path.stem}_lossless_spec.md",
            )
            self._copy_template(
                source=Path("docs/codex_lossless_compilation_workfile.md"),
                destination=output_dir / f"{input_path.stem}_lossless_workfile.md",
            )
            lossless_workfile_path = output_dir / f"{input_path.stem}_lossless_workfile.md"

        lecture_workfile_path: Path | None = None
        if options.init_lecture_workfile:
            self._report(on_status, "Preparing lecture reconstruction workfile")
            self._copy_template(
                source=Path("docs/lecture_note_generation_spec.md"),
                destination=output_dir / f"{input_path.stem}_lecture_spec.md",
            )
            self._copy_template(
                source=Path("docs/codex_closed_loop_lecture_workfile.md"),
                destination=output_dir / f"{input_path.stem}_lecture_workfile.md",
            )
            lecture_workfile_path = output_dir / f"{input_path.stem}_lecture_workfile.md"

        self._report(on_status, "Workflow finished")
        return WorkbenchResult(
            artifact_root=artifact_root,
            asset_dir=artifact_root / "assets",
            ir_path=ir_path,
            qa_json_path=qa_json_path,
            qa_md_path=qa_md_path,
            docx_path=docx_path,
            html_path=html_path,
            lossless_workfile_path=lossless_workfile_path,
            lecture_workfile_path=lecture_workfile_path,
            html_note=html_note,
        )

    @staticmethod
    def _copy_template(source: Path, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        return destination

    @staticmethod
    def _report(on_status: StatusCallback | None, message: str) -> None:
        if on_status:
            on_status(message)
