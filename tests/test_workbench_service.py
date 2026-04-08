from __future__ import annotations

from app.config import load_config
from app.services.workbench_service import WorkbenchOptions, WorkbenchService
from tests.sample_factory import build_sample_pptx


def test_workbench_service_builds_bundle_with_handoffs(tmp_path):
    pptx_path = build_sample_pptx(tmp_path / "demo_course.pptx")
    config = load_config(overrides={"output_dir": tmp_path / "artifacts"})
    service = WorkbenchService(config)

    result = service.build_bundle(
        pptx_path,
        tmp_path / "studio_runs",
        WorkbenchOptions(
            export_docx=True,
            export_html=True,
            init_lossless_workfile=True,
            init_lecture_workfile=True,
        ),
    )

    assert result.docx_path and result.docx_path.exists()
    assert result.html_path and result.html_path.exists()
    assert result.ir_path.exists()
    assert result.qa_md_path.exists()
    assert result.lossless_workfile_path and result.lossless_workfile_path.exists()
    assert result.lecture_workfile_path and result.lecture_workfile_path.exists()
    assert any(path.suffix == ".png" for path in result.asset_dir.rglob("*"))
