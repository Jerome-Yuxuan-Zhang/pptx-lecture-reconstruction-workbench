from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from nicegui import events, run, ui

from app.config import AppConfig, load_config
from app.services.workbench_service import (
    WorkbenchOptions,
    WorkbenchResult,
    WorkbenchService,
)
from app.utils.file_utils import ensure_directory

CUSTOM_HEAD = """
<style>
  :root {
    --paper: #f6f1e7;
    --card: rgba(255, 252, 247, 0.86);
    --ink: #182028;
    --muted: #5c645c;
    --forest: #1d5f46;
    --leaf: #92b59f;
    --ochre: #b96d2f;
    --rule: rgba(24, 32, 40, 0.08);
    --shadow: 0 30px 70px rgba(25, 36, 29, 0.12);
  }

  body {
    background:
      radial-gradient(circle at top left, rgba(185,109,47,0.18), transparent 22rem),
      radial-gradient(circle at 85% 8%, rgba(29,95,70,0.16), transparent 18rem),
      linear-gradient(180deg, #efe6d6 0%, var(--paper) 28rem, #fdfaf5 100%);
    color: var(--ink);
    font-family: "Aptos", "Segoe UI Variable Text", "Trebuchet MS", sans-serif;
  }

  h1, h2, h3, .studio-serif {
    font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
    letter-spacing: -0.02em;
  }

  .studio-shell {
    width: min(1380px, calc(100vw - 32px));
    margin: 20px auto 40px;
  }

  .hero-card,
  .glass-card {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.6);
    box-shadow: var(--shadow);
    backdrop-filter: blur(14px);
    border-radius: 28px;
  }

  .hero-card {
    position: relative;
    overflow: hidden;
  }

  .hero-card::after {
    content: "";
    position: absolute;
    right: -80px;
    top: -60px;
    width: 260px;
    height: 260px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(29,95,70,0.18), transparent 70%);
    pointer-events: none;
  }

  .stage-pill {
    border: 1px solid rgba(29,95,70,0.14);
    border-radius: 999px;
    background: rgba(255,255,255,0.75);
    color: var(--forest);
    padding: 8px 14px;
    font-weight: 600;
    letter-spacing: 0.01em;
  }

  .section-title {
    color: var(--forest);
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
  }

  .section-kicker {
    color: var(--muted);
    font-size: 0.95rem;
  }

  .log-strip {
    border: 1px solid rgba(29,95,70,0.1);
    background: rgba(247, 250, 246, 0.8);
    border-radius: 18px;
    padding: 12px 14px;
    color: var(--ink);
  }

  .path-card {
    border-radius: 20px;
    border: 1px solid var(--rule);
    background: rgba(255,255,255,0.82);
  }

  .preview-tile {
    overflow: hidden;
    border-radius: 22px;
    border: 1px solid rgba(29,95,70,0.12);
    background: rgba(255,255,255,0.74);
  }

  .hint-panel {
    border-left: 5px solid var(--ochre);
    background: rgba(255, 248, 239, 0.9);
    border-radius: 18px;
  }
</style>
"""


def _normalize_path(raw_value: str) -> Path:
    path = Path(raw_value.strip()).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def _open_path(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
        return
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
        return
    subprocess.Popen(["xdg-open", str(path)])


def _image_to_data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/{path.suffix.lstrip('.')};base64,{encoded}"


def _open_browser_later(url: str, delay_seconds: float = 1.2) -> None:
    def _runner() -> None:
        time.sleep(delay_seconds)
        webbrowser.open(url)

    threading.Thread(target=_runner, daemon=True).start()


def _load_qa_summary(result: WorkbenchResult) -> dict:
    if not result.qa_json_path.exists():
        return {}
    return json.loads(result.qa_json_path.read_text(encoding="utf-8"))


def _render_result_card(
    title: str,
    path: Path,
    description: str,
    open_label: str = "Open",
) -> None:
    with ui.card().classes("path-card w-full p-4 gap-2"):
        ui.label(title).classes("studio-serif text-lg font-semibold text-[#173a2c]")
        ui.label(description).classes("text-sm text-[#5c645c]")
        ui.label(str(path)).classes("text-xs text-[#45505a] break-all")
        with ui.row().classes("items-center gap-2 mt-2"):
            ui.button(open_label, on_click=lambda p=path: _open_path(p)).props("flat color=primary")
            ui.button(
                "Reveal Folder",
                on_click=lambda p=path.parent: _open_path(p),
            ).props("outline color=secondary")


def _build_workspace_page(config: AppConfig, service: WorkbenchService) -> None:
    ui.add_head_html(CUSTOM_HEAD)

    uploads_dir = ensure_directory(config.output_dir / "_studio_uploads")
    selected_upload: dict[str, Path | None] = {"path": None}
    default_output_dir = ensure_directory(config.output_dir / "studio_runs")

    ui.query("body").classes("bg-transparent")

    with ui.column().classes("studio-shell gap-5"):
        with ui.card().classes("hero-card w-full p-8 md:p-10 gap-5"):
            ui.label("Lecture Reconstruction Studio").classes(
                "studio-serif text-4xl md:text-5xl font-bold text-[#173a2c]"
            )
            ui.label(
                "No tkinter. Local-first. Beautiful enough to live in your daily workflow."
            ).classes("text-lg text-[#41514b]")
            ui.markdown(
                "**Three stages, one workbench:** parse the deck, preserve everything into "
                "a no-loss draft, then hand Codex a clean closed-loop lecture package."
            ).classes("text-[15px] text-[#304038]")
            with ui.row().classes("gap-3 flex-wrap"):
                ui.html('<span class="stage-pill">Stage 1 · Parse + QA</span>')
                ui.html('<span class="stage-pill">Stage 2 · Lossless Compiler</span>')
                ui.html('<span class="stage-pill">Stage 3 · Closed-loop Lecture</span>')

        with ui.row().classes("w-full gap-5 items-stretch no-wrap max-[1100px]:flex-col"):
            with ui.card().classes("glass-card w-[42%] max-[1100px]:w-full p-6 gap-4"):
                ui.label("Input Control").classes("section-title")
                ui.label(
                    "Choose a local PPTX or upload one here, then let the workbench create your bundle."
                ).classes("section-kicker")

                input_path = ui.input("PPTX path").props("outlined clearable").classes("w-full")
                input_path.value = str(Path.cwd() / "samples/sample_ppt/demo_course.pptx")

                with ui.row().classes("gap-2 flex-wrap"):
                    ui.button(
                        "Use Demo Deck",
                        on_click=lambda: setattr(
                            input_path,
                            "value",
                            str(Path.cwd() / "samples/sample_ppt/demo_course.pptx"),
                        ),
                    ).props("outline color=primary")
                    ui.button(
                        "Use Uploaded File",
                        on_click=lambda: setattr(
                            input_path,
                            "value",
                            str(selected_upload["path"]) if selected_upload["path"] else "",
                        ),
                    ).props("outline color=secondary")

                upload_state = ui.label("No uploaded file yet").classes("text-sm text-[#5c645c]")

                def on_upload(event: events.UploadEventArguments) -> None:
                    if Path(event.name).suffix.lower() != ".pptx":
                        ui.notify("Please upload a .pptx file.", color="negative")
                        return
                    destination = uploads_dir / event.name
                    destination.write_bytes(event.content.read())
                    selected_upload["path"] = destination
                    upload_state.set_text(f"Uploaded: {destination}")
                    input_path.value = str(destination)
                    ui.notify(f"Loaded {event.name}", color="positive")

                ui.upload(on_upload=on_upload, auto_upload=True).props("accept=.pptx").classes(
                    "w-full"
                )

                output_path = ui.input("Output workspace").props("outlined").classes("w-full")
                output_path.value = str(default_output_dir)

                ui.separator()

                ui.label("Bundle Options").classes("section-title")
                export_docx = ui.switch("Export DOCX", value=True)
                export_html = ui.switch("Generate offline HTML draft", value=True)
                lossless_workfile = ui.switch("Prepare lossless Codex handoff", value=True)
                lecture_workfile = ui.switch("Prepare lecture Codex handoff", value=True)

                with ui.card().classes("hint-panel w-full p-4 gap-2"):
                    ui.label("Best practice").classes("font-semibold text-[#6d4318]")
                    ui.label(
                        "Run the lossless handoff and lecture handoff together. You can give Codex "
                        "the no-loss workfile first, then the closed-loop workfile."
                    ).classes("text-sm text-[#5f4a2b]")

                run_button = ui.button("Build Workbench Bundle").props(
                    "color=primary size=lg unelevated"
                )

            with ui.column().classes("w-[58%] max-[1100px]:w-full gap-5"):
                with ui.card().classes("glass-card w-full p-6 gap-4"):
                    ui.label("Status Console").classes("section-title")
                    status_line = ui.label("Ready for a deck.").classes(
                        "text-base text-[#304038] font-medium"
                    )
                    spinner = ui.spinner(size="lg", color="primary")
                    spinner.visible = False
                    activity_log = ui.column().classes("w-full gap-2")

                with ui.card().classes("glass-card w-full p-6 gap-4"):
                    ui.label("Bundle Output").classes("section-title")
                    summary_row = ui.row().classes("w-full gap-3 flex-wrap")
                    result_cards = ui.column().classes("w-full gap-3")
                    preview_gallery = ui.row().classes("w-full gap-4 flex-wrap")

        def render_log(lines: list[str]) -> None:
            activity_log.clear()
            for line in lines:
                with activity_log:
                    ui.label(line).classes("log-strip w-full text-sm")

        def render_results(result: WorkbenchResult) -> None:
            summary_row.clear()
            result_cards.clear()
            preview_gallery.clear()

            summary = _load_qa_summary(result)
            slide_count = summary.get("slide_count", "n/a")
            degraded = len(summary.get("degraded_blocks", []))
            block_counts = summary.get("block_counts", {})

            stats = [
                ("Slides", str(slide_count)),
                ("Degraded Blocks", str(degraded)),
                ("Text Blocks", str(block_counts.get("text", 0))),
                ("Diagram Assets", str(len(list(result.asset_dir.rglob("*.png"))))),
            ]
            for label, value in stats:
                with (
                    summary_row,
                    ui.card().classes("path-card min-w-[150px] p-4 items-start gap-1"),
                ):
                    ui.label(value).classes("studio-serif text-2xl font-bold text-[#173a2c]")
                    ui.label(label).classes("text-sm text-[#5c645c]")

            with result_cards:
                if result.docx_path:
                    _render_result_card(
                        "DOCX Export",
                        result.docx_path,
                        "Editable Word output with images, tables, and diagram previews.",
                    )
                if result.html_path:
                    _render_result_card(
                        "Offline HTML Draft",
                        result.html_path,
                        result.html_note or "Offline lecture draft generated from IR.",
                    )
                _render_result_card(
                    "IR JSON",
                    result.ir_path,
                    "Layout-aware intermediate representation for downstream processing.",
                )
                _render_result_card(
                    "QA Markdown",
                    result.qa_md_path,
                    "Human-readable extraction report with degraded block notes.",
                )
                if result.lossless_workfile_path:
                    _render_result_card(
                        "Lossless Codex Workfile",
                        result.lossless_workfile_path,
                        "Hand this to Codex first when you want a no-loss compilation pass.",
                    )
                if result.lecture_workfile_path:
                    _render_result_card(
                        "Lecture Codex Workfile",
                        result.lecture_workfile_path,
                        "Use this after the no-loss draft for closed-loop lecture reconstruction.",
                    )

            preview_paths = sorted(result.asset_dir.rglob("*.png"))[:6]
            for path in preview_paths:
                with preview_gallery, ui.card().classes("preview-tile w-[290px] p-3 gap-2"):
                    ui.image(_image_to_data_url(path)).classes("w-full rounded-xl")
                    ui.label(path.name).classes("text-sm font-medium text-[#173a2c]")
                    ui.label(str(path.parent)).classes("text-xs text-[#5c645c] break-all")

        async def build_bundle() -> None:
            raw_input = input_path.value or ""
            if not raw_input.strip():
                ui.notify("Choose a PPTX path or upload a deck first.", color="negative")
                return

            try:
                normalized_input = _normalize_path(raw_input)
            except Exception as exc:  # noqa: BLE001
                ui.notify(f"Invalid input path: {exc}", color="negative")
                return
            if not normalized_input.exists():
                ui.notify("That PPTX path does not exist.", color="negative")
                return
            if normalized_input.suffix.lower() != ".pptx":
                ui.notify("Only .pptx files are supported in the GUI for now.", color="negative")
                return

            try:
                normalized_output = _normalize_path(output_path.value or str(default_output_dir))
            except Exception as exc:  # noqa: BLE001
                ui.notify(f"Invalid output path: {exc}", color="negative")
                return

            status_line.set_text("Running the full bundle workflow...")
            spinner.visible = True
            run_button.disable()
            render_log([])
            summary_row.clear()
            result_cards.clear()
            preview_gallery.clear()

            lines: list[str] = []
            options = WorkbenchOptions(
                export_docx=bool(export_docx.value),
                export_html=bool(export_html.value),
                init_lossless_workfile=bool(lossless_workfile.value),
                init_lecture_workfile=bool(lecture_workfile.value),
            )

            try:
                result = await run.io_bound(
                    service.build_bundle,
                    normalized_input,
                    normalized_output,
                    options,
                    lines.append,
                )
            except Exception as exc:  # noqa: BLE001
                status_line.set_text("Workbench failed.")
                render_log(lines + [f"Error: {exc}"])
                ui.notify(f"Bundle failed: {exc}", color="negative")
            else:
                status_line.set_text("Bundle complete. Open the files on the right.")
                render_log(lines)
                render_results(result)
                ui.notify("Workbench bundle is ready.", color="positive")
            finally:
                spinner.visible = False
                run_button.enable()

        run_button.on_click(build_bundle)


def launch_gui(
    config_path: Path | None = None,
    host: str = "127.0.0.1",
    port: int = 8181,
    auto_open_browser: bool = False,
) -> None:
    config = load_config(config_path)
    service = WorkbenchService(config)

    ui.colors(
        primary="#1d5f46",
        secondary="#b96d2f",
        accent="#8aa39a",
        positive="#2f7d56",
        warning="#b07a1e",
        negative="#b6413c",
    )

    @ui.page("/")
    def main_page() -> None:
        _build_workspace_page(config, service)

    if auto_open_browser:
        _open_browser_later(f"http://{host}:{port}")

    ui.run(
        host=host,
        port=port,
        reload=False,
        title="Lecture Reconstruction Studio",
        favicon="book",
        show=False,
    )
