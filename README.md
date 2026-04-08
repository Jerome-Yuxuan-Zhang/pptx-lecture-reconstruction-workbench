# PPT Extractor With Layouting

Offline-first PPTX to DOCX extraction and lecture reconstruction workbench for VSCode Codex, with IR, QA, and diagram fallback assets.

这是一个面向课程整理场景的本地工作台，核心目标不是“快速总结”，而是：

- 先把 PPT / 讲义 / 截图材料尽量**结构化提取**
- 再把材料编译成**无损、可审计、可续传**的底稿
- 最后再进入**闭环讲义重构**

## What This Repo Does

- Parse `.pptx` into text, tables, images, and diagram fallback assets
- Build a layout-aware IR with reading order, titles, captions, and QA reports
- Export `.docx`, `slide_ir.json`, `qa_report.{json,md}`
- Downgrade complex shapes into reusable `SVG + PNG preview` assets instead of dropping them
- Provide Codex-ready specs, prompts, and workfiles for:
  - lossless course material compilation
  - closed-loop lecture reconstruction

## Recommended Workflow

这个项目现在建议固定成两阶段：

### Stage 1: Lossless Compiler

目标：先做**无损底稿**，不做总结，不提前丢信息。

读取：

- 原始 PPT / PDF / OCR / 课堂转写
- `slide_ir.json`
- `qa_report.md`
- `assets/`

输出：

- Source Register
- Lossless Transcription
- Structured Reorganization
- Concept Index
- Dependency Map
- Ambiguity & Risk Log
- No-loss Audit Checklist
- Continuation Protocol

对应文件：

- [docs/lossless_course_material_compiler_spec.md](docs/lossless_course_material_compiler_spec.md)
- [docs/codex_lossless_compilation_workfile.md](docs/codex_lossless_compilation_workfile.md)
- [prompts/lossless_course_material_compiler_prompt.md](prompts/lossless_course_material_compiler_prompt.md)

### Stage 2: Closed-loop Lecture Reconstruction

目标：在不失去信息的前提下，把底稿重构为闭环、可打印的 HTML 讲义。

对应文件：

- [docs/lecture_note_generation_spec.md](docs/lecture_note_generation_spec.md)
- [docs/codex_closed_loop_lecture_workfile.md](docs/codex_closed_loop_lecture_workfile.md)
- [prompts/lecture_reconstruction_prompt.md](prompts/lecture_reconstruction_prompt.md)

一句话建议：

1. 先无损编译
2. 再讲义重构

不要直接跳过 Stage 1。

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

## CLI

### Parse PPTX and export DOCX

```bash
python -m app.cli ppt2docx samples/sample_ppt/demo_course.pptx --output samples/expected_outputs/demo_course.docx
```

### Extract IR only

```bash
python -m app.cli extract-ir samples/sample_ppt/demo_course.pptx --output artifacts
```

### Initialize lecture reconstruction spec

```bash
python -m app.cli init-lecture-spec
```

### Initialize lossless compiler spec

```bash
python -m app.cli init-lossless-spec
```

### Initialize Codex lecture workfile

```bash
python -m app.cli init-codex-workfile
```

### Initialize Codex lossless workfile

```bash
python -m app.cli init-lossless-workfile
```

### Generate offline HTML draft

```bash
python -m app.cli lecture-generate artifacts/demo_course/slide_ir.json
```

### Launch the GUI workbench

```bash
python -m app.cli gui --host 127.0.0.1 --port 8181
```

### Launch from a root entry file

```bash
python start.py
```

Windows 下也可以直接双击：

```text
start_gui.bat
```

### Run QA

```bash
python -m app.cli qa-check artifacts/demo_course
```

## VSCode + Codex

### If you want a no-loss source-preserving draft

让 Codex 同时读取：

- `docs/lossless_course_material_compiler_spec.md`
- `docs/codex_lossless_compilation_workfile.md`

### If you want a final closed-loop lecture

让 Codex 同时读取：

- `docs/lecture_note_generation_spec.md`
- `docs/codex_closed_loop_lecture_workfile.md`

### Best practice

先跑：

```bash
python -m app.cli extract-ir your_lecture.pptx --output artifacts
python -m app.cli init-lossless-workfile
python -m app.cli init-codex-workfile
```

然后：

1. 先做无损编译
2. 再做闭环讲义

## Key Outputs

- `slide_ir.json`
- `qa_report.md`
- `assets/*.svg`
- `assets/*.png`
- `.docx`
- offline `.html`

## GUI Workbench

本地 GUI 不是 `tkinter`，而是一个本地 Web workbench。它直接复用项目已有的提取、QA、DOCX、HTML 和 Codex handoff 服务层。

你可以在界面里完成：

- 选择或上传 `.pptx`
- 一键生成 IR / QA / DOCX / HTML
- 一键准备 lossless workfile 和 lecture workfile
- 查看 diagram fallback 预览图
- 直接打开生成文件和输出目录
- 通过 `start.py` 或 `start_gui.bat` 直接启动，不用记 CLI 命令

## Fonts

- Latin default: `Times New Roman`
- CJK default: `Noto Serif SC`

如果机器没有 `Noto Serif SC`，可以在 `.env` 或 `config.example.yaml` 中改为回退字体。

## FAQ

### Why not summarize directly?

因为“无损整理”和“简洁总结”天然冲突。这个项目的设计是：

- first preserve
- then reorganize
- then reconstruct

### Why keep diagram fallback assets?

因为复杂 shape 很容易在整理阶段被静默丢失。这里会尽量保留为 `SVG + PNG preview`，供 DOCX、后续讲义和人工复核继续使用。

### Is API the main direction?

不是。当前仓库聚焦本地工作流和 VSCode + Codex 协作。服务化可以以后再补。
