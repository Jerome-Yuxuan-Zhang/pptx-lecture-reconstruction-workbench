from __future__ import annotations

from pathlib import Path

from app.config import load_config
from app.parsers.ppt_parser import PPTParser
from tests.sample_factory import build_sample_pptx


def test_parser_extracts_text_image_table_and_titles(tmp_path):
    pptx_path = build_sample_pptx(tmp_path / "demo_course.pptx")
    parser = PPTParser(load_config(), asset_dir=tmp_path / "assets")
    document_ir = parser.parse(pptx_path)

    assert document_ir.metadata.slide_count == 2
    assert document_ir.slides[0].title == "概率论导论"

    slide1_types = {block.block_type for block in document_ir.slides[0].blocks}
    slide2_types = {block.block_type for block in document_ir.slides[1].blocks}

    assert "image" in slide1_types
    assert "table" in slide2_types
    assert "diagram" in slide2_types

    image_block = next(
        block for block in document_ir.slides[0].blocks if block.block_type == "image"
    )
    assert any(relation.relation_type == "has-caption" for relation in image_block.relations)

    diagram_block = next(
        block for block in document_ir.slides[1].blocks if block.block_type == "diagram"
    )
    assert diagram_block.content["asset_mode"] == "svg+preview"
    assert Path(diagram_block.content["svg_path"]).exists()
    assert Path(diagram_block.content["preview_path"]).exists()
