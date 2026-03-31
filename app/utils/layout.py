from __future__ import annotations

from collections.abc import Iterable

from app.models.ir_models import BoundingBox, ContentBlock


def overlaps_vertically(a: BoundingBox, b: BoundingBox, tolerance: float = 6.0) -> bool:
    return not (a.bottom + tolerance < b.y or b.bottom + tolerance < a.y)


def reading_sort_key(block: ContentBlock, slide_width_pt: float) -> tuple[float, float, int]:
    band_height = max(block.bbox.height, 18.0)
    row = round(block.bbox.y / band_height, 1)
    column_hint = 0 if block.bbox.center_x < slide_width_pt * 0.52 else 1
    return (row, column_hint, int(block.bbox.x))


def sort_blocks_for_reading(
    blocks: Iterable[ContentBlock], slide_width_pt: float
) -> list[ContentBlock]:
    return sorted(blocks, key=lambda block: reading_sort_key(block, slide_width_pt))


def distance_below(anchor: BoundingBox, other: BoundingBox) -> float:
    if other.y < anchor.bottom:
        return float("inf")
    return other.y - anchor.bottom


def horizontal_overlap_ratio(a: BoundingBox, b: BoundingBox) -> float:
    overlap = max(0.0, min(a.right, b.right) - max(a.x, b.x))
    span = min(a.width, b.width) or 1.0
    return overlap / span
