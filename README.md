# PPT Extractor With Layouting

一个离线优先、可审计、可扩展的 `PPTX -> IR -> DOCX / HTML` 工程项目，面向学术课件整理、复杂图形降级保留，以及在 VSCode 中直接驱动 Codex 做闭环讲义重构。

## 功能列表

- 解析 `.pptx` 文件并提取文本、表格、图片与图形信息
- 基于统一 IR（Intermediate Representation）重建阅读顺序与标题层级
- 导出 `slide_ir.json`、`qa_report.{json,md}` 与 `.docx`
- 对复杂 shape 导出 `SVG + PNG preview` 降级资产，而不是静默丢弃
- 提供离线 HTML 讲义草稿生成能力
- 附带可直接给 VSCode Codex 加载的闭环讲义工作单
- 在 README 中保留 API 未来方向说明，但当前实现聚焦本地工作流

## 技术栈

- Python 3.11+
- `python-pptx`
- `python-docx`
- `pydantic`
- `typer`
- `jinja2`
- `pytest`
- `ruff`
- `black`

## 安装步骤

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

可选配置：

1. 复制 `.env.example` 为 `.env`
2. 或参考 `config.example.yaml` 创建本地配置文件

## 本地运行

PPT 转 DOCX：

```bash
python -m app.cli ppt2docx samples/sample_ppt/demo_course.pptx --output samples/expected_outputs/demo_course.docx
```

仅提取 IR：

```bash
python -m app.cli extract-ir samples/sample_ppt/demo_course.pptx --output artifacts
```

生成离线 HTML 讲义：

```bash
python -m app.cli lecture-generate artifacts/demo_course/slide_ir.json
```

初始化给 Codex 直接使用的工作单：

```bash
python -m app.cli init-codex-workfile
```

运行测试：

```bash
pytest
```

## CLI 示例

- `python -m app.cli ppt2docx input.pptx --output output.docx`
- `python -m app.cli extract-ir input.pptx --output artifacts`
- `python -m app.cli init-lecture-spec`
- `python -m app.cli init-codex-workfile`
- `python -m app.cli lecture-generate artifacts/demo/slide_ir.json --use-llm`
- `python -m app.cli qa-check artifacts/demo`

## VSCode + Codex 工作流

1. 先跑 `extract-ir` 或 `ppt2docx`，拿到 `slide_ir.json`、`qa_report.md` 和 `assets/`
2. 再跑 `python -m app.cli init-codex-workfile`
3. 打开 [docs/codex_closed_loop_lecture_workfile.md](/d:/Github_Proj/ppt_extractor_with_layouting/docs/codex_closed_loop_lecture_workfile.md) 或你刚生成的副本
4. 把输入材料路径改成你的真实文件
5. 在 VSCode 里让 Codex 同时读取这个工作单和 [docs/lecture_note_generation_spec.md](/d:/Github_Proj/ppt_extractor_with_layouting/docs/lecture_note_generation_spec.md)

## API 预留说明

当前仓库不再把 API 作为主实现方向。若未来需要服务化，可以再补 FastAPI 或任务队列；本阶段只在 README 中保留这个演进方向，不让它干扰本地讲义工作流。

## 字体说明

- 英文字体默认使用 `Times New Roman`
- 中文字体默认使用 `Noto Serif SC`
- 如果本机缺少 `Noto Serif SC`，可在 `.env` 或 `config.yaml` 中改用 `SimSun`、`Microsoft YaHei` 等回退字体
- 本项目在 DOCX 导出阶段做了 run-level 的中英字体设置，但最终显示仍受本机 Word 与字体安装情况影响

## 常见问题

**1. 为什么复杂图形没有完全还原？**

第一阶段重点是稳定、可解释地输出结构化内容。复杂矢量图会被降级为 `SVG + PNG preview` 资产，并写入 IR 与 QA 报告；DOCX 会优先插入 preview 图。

**2. 为什么检测到 API Key 也不会直接联网调用？**

项目默认离线优先。只有用户显式启用 `--use-llm`，且你补上具体 provider 适配器时，才建议调用外部模型。

**3. 能否支持 `.ppt`？**

当前主链路只保证 `.pptx`。`.ppt` 建议先用 LibreOffice 等工具转为 `.pptx`。

## 未来路线图

1. 更强的多栏版面分析与图文关系识别
2. SmartArt / group shape 更高保真 SVG 重建
3. 真正可插拔的 OpenAI / Claude / Gemini provider
4. 更完整的 HTML 讲义闭环与自检生成
5. 按需要再补轻量 API 或批处理服务
