from __future__ import annotations

from app.models.ir_models import BlockRelation, ContentBlock, SlideDocument
from app.utils.layout import distance_below, horizontal_overlap_ratio, sort_blocks_for_reading


class IRBuilder:
    """Post-process raw blocks into a stable, layout-aware slide IR."""

    def refine_slide(self, slide: SlideDocument) -> SlideDocument:
        blocks = sort_blocks_for_reading(slide.blocks, slide.width_pt or 1.0)
        self._assign_semantic_roles(slide, blocks)
        self._attach_caption_relations(blocks)
        slide.blocks = blocks
        slide.title = next(
            (block.content.get("text") for block in blocks if block.semantic_role == "title"), None
        )
        return slide

    def _assign_semantic_roles(self, slide: SlideDocument, blocks: list[ContentBlock]) -> None:
        text_blocks = [block for block in blocks if block.block_type == "text"]
        if not text_blocks:
            return

        top_blocks = sorted(
            text_blocks, key=lambda block: (block.bbox.y, -float(block.style.font_size_pt or 0))
        )
        title_candidate = max(
            top_blocks[:3],
            key=lambda block: (
                1 if block.style.is_placeholder_title else 0,
                float(block.style.font_size_pt or 0),
                -block.bbox.y,
            ),
        )
        if title_candidate.bbox.y <= (slide.height_pt or 0) * 0.3:
            title_candidate.semantic_role = "title"

        for block in text_blocks:
            if block.block_id == title_candidate.block_id:
                continue
            if (
                block.bbox.y >= (slide.height_pt or 0) * 0.88
                and (block.style.font_size_pt or 0) <= 11
            ):
                block.semantic_role = "footer"
            elif (block.style.font_size_pt or 0) >= max(
                (title_candidate.style.font_size_pt or 0) - 2, 14
            ):
                if block.bbox.y <= (slide.height_pt or 0) * 0.4:
                    block.semantic_role = "subtitle"
            elif (
                len((block.content.get("text") or "").strip()) < 80
                and block.bbox.width <= (slide.width_pt or 0) * 0.7
            ):
                block.semantic_role = "body"

    def _attach_caption_relations(self, blocks: list[ContentBlock]) -> None:
        text_blocks = [block for block in blocks if block.block_type == "text"]
        visual_blocks = [
            block for block in blocks if block.block_type in {"image", "table", "diagram"}
        ]
        for visual in visual_blocks:
            candidates = []
            for text_block in text_blocks:
                text = (text_block.content.get("text") or "").strip()
                if text_block.semantic_role == "title" or not text or len(text) > 120:
                    continue
                if horizontal_overlap_ratio(visual.bbox, text_block.bbox) < 0.35:
                    continue
                gap = distance_below(visual.bbox, text_block.bbox)
                if gap > 120:
                    continue
                score = 1 / max(gap, 1)
                candidates.append((score, text_block))
            if not candidates:
                continue
            _, caption = max(candidates, key=lambda item: item[0])
            caption.semantic_role = "caption"
            caption.relations.append(
                BlockRelation(
                    relation_type="caption-for", target_block_id=visual.block_id, score=0.9
                )
            )
            visual.relations.append(
                BlockRelation(
                    relation_type="has-caption", target_block_id=caption.block_id, score=0.9
                )
            )
