from __future__ import annotations

from pathlib import Path
from typing import Any

from app.models.ir_models import BlockStyle, BoundingBox, ContentBlock
from app.utils.diagram_assets import build_diagram_assets


def build_diagram_block(
    shape: Any,
    block_id: str,
    z_index: int,
    reason: str,
    asset_stem: Path | None = None,
    text_override: str | None = None,
) -> ContentBlock:
    bbox = BoundingBox(
        x=shape.left.pt, y=shape.top.pt, width=shape.width.pt, height=shape.height.pt
    )
    text = text_override
    if text is None:
        text = shape.text.strip() if getattr(shape, "has_text_frame", False) else ""
    shape_type = getattr(shape.shape_type, "name", str(shape.shape_type))
    description = f"Unsupported shape downgraded from PPT object: {shape_type}"
    warnings = [reason]
    content = {
        "text": text,
        "description": description,
    }
    if asset_stem is not None:
        content.update(
            build_diagram_assets(
                shape_type=shape_type,
                bbox=bbox,
                output_stem=asset_stem,
                text=text,
                description=description,
            )
        )
    return ContentBlock(
        block_id=block_id,
        block_type="diagram",
        bbox=bbox,
        z_index=z_index,
        semantic_role="body" if text else "decorative",
        content=content,
        style=BlockStyle(shape_type=shape_type),
        source_shape_name=shape.name,
        warnings=warnings,
    )
