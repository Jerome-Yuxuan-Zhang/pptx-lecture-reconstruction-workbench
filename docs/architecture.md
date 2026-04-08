# Architecture

## Goal

本项目采用离线优先、IR 驱动、本地工作台优先的结构，目标不是直接做“摘要”，而是把课程材料处理成两个连续阶段：

1. 无损课程材料编译
2. 闭环讲义重构

这样可以先尽量保住信息，再进入讲义层重组，减少模型在“整理”时偷做压缩的风险。

## Pipeline

### Stage 1: Source Extraction

输入：

- `.pptx`

输出：

- `slide_ir.json`
- `qa_report.{json,md}`
- `assets/`

主要模块：

- `app/parsers/`
- `app/builders/ir_builder.py`
- `app/services/export_service.py`
- `app/services/qa_service.py`

### Stage 2: Lossless Course Material Compilation

目标：

- 不删减
- 不压缩
- 不总结
- 只做原文保留、结构化重组和全量审计

主要文档入口：

- `docs/lossless_course_material_compiler_spec.md`
- `docs/codex_lossless_compilation_workfile.md`
- `prompts/lossless_course_material_compiler_prompt.md`

### Stage 3: Closed-loop Lecture Reconstruction

目标：

- 基于无损底稿，重构成完整、可打印、闭环的 HTML 讲义

主要文档入口：

- `docs/lecture_note_generation_spec.md`
- `docs/codex_closed_loop_lecture_workfile.md`
- `prompts/lecture_reconstruction_prompt.md`

## Runtime Modules

1. `app/parsers/`
   负责从 `.pptx` 中抽取文本、表格、图片、图形和位置数据。
2. `app/builders/ir_builder.py`
   负责阅读顺序、标题识别、caption 关系等语义重建。
3. `app/builders/docx_builder.py`
   负责把 IR 输出为 DOCX。
4. `app/builders/html_builder.py`
   负责提供一个离线 HTML 草稿兜底实现。
5. `app/services/`
   负责编排导出、QA 和 LLM 预留逻辑。
6. `app/cli.py`
   负责暴露本地工作流入口，包括提取、导出和初始化 Codex 工作单。
7. `app/gui.py`
   负责提供本地 Web GUI workbench，直接复用 `WorkbenchService`，不引入单独的 GUI 业务逻辑。

## IR Design

核心对象：

- `SlideIRDocument`
- `SlideDocument`
- `ContentBlock`
- `BoundingBox`
- `BlockRelation`

设计原则：

- 先抽象语义，再决定最终导出形式
- 保留 `bbox`、`block_type`、`semantic_role`、`relations`
- 支持局部失败对象降级，不因为单个 shape 让整页崩溃

## Diagram Fallback Strategy

复杂图形不直接丢弃，而是降级成：

- `diagram` block
- `SVG` asset
- `PNG preview`

这样可以让：

- DOCX 插入 preview
- Codex 在后续讲义阶段读取 SVG / preview
- 人工复核时看到完整降级痕迹

## Why Two Prompt Systems

项目里同时存在两类 Prompt，是故意的：

### Lossless Compiler Prompt

解决“先别丢信息”的问题。

### Lecture Reconstruction Prompt

解决“如何把材料重组为闭环讲义”的问题。

这两者不是重复，而是上下游。

## Future Extensions

- 更强的多栏版面分析和图文配对
- 更高保真的 SmartArt / group shape SVG 重建
- 真实的 provider adapters
- 更完整的无损编译产物落盘工具链
- 更完整的闭环 HTML 讲义生成器
