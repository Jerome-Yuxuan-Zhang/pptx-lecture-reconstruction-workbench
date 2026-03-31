from __future__ import annotations

from app.builders.ir_builder import IRBuilder
from app.config import load_config
from app.parsers.ppt_parser import PPTParser
from tests.sample_factory import build_sample_pptx


def test_ir_builder_marks_footer_and_caption(tmp_path):
    pptx_path = build_sample_pptx(tmp_path / "demo_course.pptx")
    parser = PPTParser(load_config(), asset_dir=tmp_path / "assets")
    document_ir = parser.parse(pptx_path)

    slide1 = document_ir.slides[0]
    slide2 = document_ir.slides[1]

    assert any(block.semantic_role == "footer" for block in slide1.blocks)
    assert any(block.semantic_role == "caption" for block in slide1.blocks)
    assert any(block.semantic_role == "caption" for block in slide2.blocks)

    refined = IRBuilder().refine_slide(slide2)
    assert refined.title == "离散型随机变量"
