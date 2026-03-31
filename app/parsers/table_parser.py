from __future__ import annotations

from typing import Any

from app.models.ir_models import BlockStyle, BoundingBox, ContentBlock, TableCellContent


def build_table_block(shape: Any, block_id: str, z_index: int) -> ContentBlock:
    rows = len(shape.table.rows)
    cols = len(shape.table.columns)
    cells: list[TableCellContent] = []

    for row_idx, row in enumerate(shape.table.rows):
        for col_idx, cell in enumerate(row.cells):
            if getattr(cell, "is_spanned", False):
                continue
            row_span = getattr(cell, "span_height", 1) or 1
            col_span = getattr(cell, "span_width", 1) or 1
            cells.append(
                TableCellContent(
                    row=row_idx,
                    col=col_idx,
                    text=cell.text.strip(),
                    row_span=row_span,
                    col_span=col_span,
                )
            )

    bbox = BoundingBox(
        x=shape.left.pt, y=shape.top.pt, width=shape.width.pt, height=shape.height.pt
    )
    return ContentBlock(
        block_id=block_id,
        block_type="table",
        bbox=bbox,
        z_index=z_index,
        semantic_role="body",
        content={
            "rows": rows,
            "cols": cols,
            "cells": [cell.model_dump() for cell in cells],
        },
        style=BlockStyle(shape_type=getattr(shape.shape_type, "name", str(shape.shape_type))),
        source_shape_name=shape.name,
    )
