from __future__ import annotations

from pathlib import Path

from app.models.ir_models import SlideIRDocument
from app.utils.file_utils import dump_json


class QAService:
    def build_report(self, document_ir: SlideIRDocument, artifact_root: Path) -> tuple[Path, Path]:
        degraded = []
        missing_titles = []
        counts: dict[str, int] = {}
        for slide in document_ir.slides:
            if not slide.title:
                missing_titles.append(slide.slide_index)
            for block in slide.blocks:
                counts[block.block_type] = counts.get(block.block_type, 0) + 1
                if block.warnings:
                    degraded.append(
                        {
                            "slide_index": slide.slide_index,
                            "block_id": block.block_id,
                            "warnings": block.warnings,
                        }
                    )
        payload = {
            "source": document_ir.metadata.source_name,
            "slide_count": document_ir.metadata.slide_count,
            "block_counts": counts,
            "missing_titles": missing_titles,
            "degraded_blocks": degraded,
        }
        json_path = dump_json(artifact_root / "qa_report.json", payload)
        markdown = [
            f"# QA Report: {document_ir.metadata.source_name}",
            "",
            f"- Slide count: {document_ir.metadata.slide_count}",
            f"- Missing titles: {missing_titles or 'None'}",
            f"- Block counts: {counts}",
            "",
            "## Degraded Blocks",
        ]
        if degraded:
            markdown.extend(
                [
                    f"- Slide {item['slide_index']} | {item['block_id']} | {', '.join(item['warnings'])}"
                    for item in degraded
                ]
            )
        else:
            markdown.append("- None")
        md_path = artifact_root / "qa_report.md"
        md_path.write_text("\n".join(markdown), encoding="utf-8")
        return json_path, md_path
