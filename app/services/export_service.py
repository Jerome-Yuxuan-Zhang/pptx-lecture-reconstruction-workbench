from __future__ import annotations

from pathlib import Path

from app.builders.docx_builder import DocxBuilder
from app.config import AppConfig
from app.models.ir_models import SlideIRDocument
from app.parsers.ppt_parser import PPTParser
from app.utils.file_utils import dump_json, ensure_directory


class ExportService:
    def __init__(self, config: AppConfig):
        self.config = config

    def parse_pptx(
        self, input_path: Path, artifact_root: Path | None = None
    ) -> tuple[SlideIRDocument, Path]:
        root = ensure_directory(artifact_root or self.config.output_dir / input_path.stem)
        asset_dir = ensure_directory(root / "assets")
        parser = PPTParser(self.config, asset_dir=asset_dir)
        return parser.parse(input_path), root

    def export_ir(self, document_ir: SlideIRDocument, artifact_root: Path) -> Path:
        return dump_json(artifact_root / "slide_ir.json", document_ir.model_dump(mode="json"))

    def export_docx(self, document_ir: SlideIRDocument, output_path: Path) -> Path:
        builder = DocxBuilder(self.config)
        return builder.build(document_ir, output_path)
