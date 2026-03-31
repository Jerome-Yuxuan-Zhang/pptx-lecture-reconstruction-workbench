# Architecture

## 目标

项目采用离线优先、IR 驱动、本地工作台优先的结构，保证 `PPTX -> Word` 主流程稳定可用，同时为 VSCode + Codex 的闭环讲义重构留出清晰入口。

## 模块分层

1. `app/parsers/`
   负责从 `.pptx` 中抽取原始对象，识别文本、表格、图片、图形，并尽量保留坐标与样式。
2. `app/builders/ir_builder.py`
   负责将原始对象整理成统一 IR，补标题角色、阅读顺序、图文 caption 关系等语义。
3. `app/builders/docx_builder.py`
   基于 IR 输出 DOCX，做页面、字体、表格、图片与标题样式控制。
4. `app/builders/html_builder.py`
   基于 IR 生成离线 HTML 草稿，作为讲义能力的无模型兜底实现。
5. `app/services/`
   编排导出、QA、任务状态与 LLM 预留逻辑，避免 CLI 与解析细节直接耦合。
6. `docs/codex_closed_loop_lecture_workfile.md`
   作为给 VSCode 中 Codex 直接加载的闭环讲义工作单，连接 IR、QA 与最终 HTML 产物。

## IR 设计

核心对象：

- `SlideIRDocument`
- `SlideDocument`
- `ContentBlock`
- `BoundingBox`
- `BlockRelation`

设计原则：

- 先抽象语义，再决定最终导出形式
- 保留 `bbox`、`block_type`、`semantic_role` 与 `relations`
- 支持失败对象降级，不因为局部错误让整页崩溃

## 降级策略

- 图片：直接导出独立资源并在 Word 中插入
- 表格：优先恢复单元格文本与合并关系
- 复杂 shape：转为 `diagram` block，并额外生成 `SVG + PNG preview` 资产
- LLM：不可用时回退到离线 HTML 生成，不阻塞本地主链路

## 扩展点

- 在 `PPTParser` 中加入更强的布局聚类算法
- 在图形降级层中加入更接近原始结构的 SVG 语义重建
- 在 `LLMService` 中接入具体 provider SDK
- 在 `HTMLBuilder` 中补更完整的数学、图示与练习生成逻辑
- 如果未来需要服务化，再补轻量 API 层
