from __future__ import annotations

from pathlib import Path

import typer

from app.config import load_config
from app.services.export_service import ExportService
from app.services.llm_service import LLMService
from app.services.qa_service import QAService
from app.services.task_service import TaskService
from app.utils.logging_utils import configure_logging

cli = typer.Typer(help="Layout-aware PPTX extraction toolkit.")


def _load_runtime(config_path: Path | None):
    config = load_config(config_path)
    configure_logging(config.log_level)
    return (
        config,
        ExportService(config),
        QAService(),
        LLMService(config),
        TaskService(config),
    )


def _copy_template(source: Path, output: Path, label: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    typer.echo(f"{label} initialized at: {output}")


@cli.command("ppt2docx")
def ppt2docx(
    input_path: Path,
    output: Path | None = typer.Option(None, "--output", "-o"),
    config_path: Path | None = typer.Option(None, "--config"),
) -> None:
    config, _, _, _, task_service = _load_runtime(config_path)
    task = task_service.run_ppt_to_docx(input_path, output)
    if task.status != "completed":
        raise typer.Exit(code=1)
    typer.echo(f"DOCX written to: {task.output_path}")
    typer.echo(f"QA report: {task.report_path}")
    if config.has_llm_credentials:
        typer.echo(
            "Detected API credentials. You may enable lecture generation with --use-llm later."
        )


@cli.command("extract-ir")
def extract_ir(
    input_path: Path,
    output: Path = typer.Option(Path("artifacts"), "--output", "-o"),
    config_path: Path | None = typer.Option(None, "--config"),
) -> None:
    _, export_service, qa_service, _, _ = _load_runtime(config_path)
    artifact_root = output / input_path.stem
    document_ir, root = export_service.parse_pptx(input_path, artifact_root)
    ir_path = export_service.export_ir(document_ir, root)
    _, qa_md = qa_service.build_report(document_ir, root)
    typer.echo(f"IR written to: {ir_path}")
    typer.echo(f"QA report: {qa_md}")


@cli.command("init-lecture-spec")
def init_lecture_spec(
    output: Path = typer.Option(Path("docs/lecture_note_generation_spec.md"), "--output", "-o"),
) -> None:
    _copy_template(Path("docs/lecture_note_generation_spec.md"), output, "Lecture spec")


@cli.command("init-lossless-spec")
def init_lossless_spec(
    output: Path = typer.Option(
        Path("docs/lossless_course_material_compiler_spec.md"), "--output", "-o"
    ),
) -> None:
    _copy_template(
        Path("docs/lossless_course_material_compiler_spec.md"),
        output,
        "Lossless compiler spec",
    )


@cli.command("init-codex-workfile")
def init_codex_workfile(
    output: Path = typer.Option(
        Path("artifacts/codex_closed_loop_lecture_workfile.md"), "--output", "-o"
    ),
) -> None:
    _copy_template(
        Path("docs/codex_closed_loop_lecture_workfile.md"),
        output,
        "Codex lecture workfile",
    )


@cli.command("init-lossless-workfile")
def init_lossless_workfile(
    output: Path = typer.Option(
        Path("artifacts/codex_lossless_compilation_workfile.md"), "--output", "-o"
    ),
) -> None:
    _copy_template(
        Path("docs/codex_lossless_compilation_workfile.md"),
        output,
        "Codex lossless workfile",
    )


@cli.command("lecture-generate")
def lecture_generate(
    input_path: Path,
    output: Path | None = typer.Option(None, "--output", "-o"),
    use_llm: bool = typer.Option(False, "--use-llm"),
    config_path: Path | None = typer.Option(None, "--config"),
) -> None:
    _, export_service, qa_service, llm_service, _ = _load_runtime(config_path)
    if input_path.suffix.lower() == ".json":
        from app.models.ir_models import SlideIRDocument

        document_ir = SlideIRDocument.model_validate_json(input_path.read_text(encoding="utf-8"))
        artifact_root = input_path.parent
    else:
        document_ir, artifact_root = export_service.parse_pptx(input_path)
        export_service.export_ir(document_ir, artifact_root)
    qa_service.build_report(document_ir, artifact_root)
    html, note = llm_service.generate_lecture_html(document_ir, use_llm=use_llm)
    html_path = output or artifact_root / f"{document_ir.metadata.source_name}.html"
    html_path.write_text(html, encoding="utf-8")
    typer.echo(f"HTML lecture written to: {html_path}")
    typer.echo(note)


@cli.command("qa-check")
def qa_check(
    target: Path,
    config_path: Path | None = typer.Option(None, "--config"),
) -> None:
    _, export_service, qa_service, _, _ = _load_runtime(config_path)
    ir_path = target / "slide_ir.json" if target.is_dir() else target
    if ir_path.suffix.lower() == ".json":
        from app.models.ir_models import SlideIRDocument

        document_ir = SlideIRDocument.model_validate_json(ir_path.read_text(encoding="utf-8"))
        artifact_root = ir_path.parent
    else:
        document_ir, artifact_root = export_service.parse_pptx(ir_path)
    _, qa_md = qa_service.build_report(document_ir, artifact_root)
    typer.echo(f"QA report written to: {qa_md}")


@cli.command("gui")
def gui(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8181, "--port"),
    config_path: Path | None = typer.Option(None, "--config"),
) -> None:
    from app.gui import launch_gui

    launch_gui(config_path=config_path, host=host, port=port)


if __name__ == "__main__":
    cli()
