from __future__ import annotations

from pathlib import Path
from typing import Any

from app.models.ir_models import BlockStyle, BoundingBox, ContentBlock


def export_picture(shape: Any, image_path: Path) -> Path:
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(shape.image.blob)
    return image_path


def build_image_block(shape: Any, block_id: str, z_index: int, image_path: Path) -> ContentBlock:
    bbox = BoundingBox(
        x=shape.left.pt, y=shape.top.pt, width=shape.width.pt, height=shape.height.pt
    )
    return ContentBlock(
        block_id=block_id,
        block_type="image",
        bbox=bbox,
        z_index=z_index,
        semantic_role="body",
        content={
            "path": str(image_path),
            "filename": image_path.name,
            "ext": shape.image.ext,
        },
        style=BlockStyle(shape_type=getattr(shape.shape_type, "name", str(shape.shape_type))),
        source_shape_name=shape.name,
    )
