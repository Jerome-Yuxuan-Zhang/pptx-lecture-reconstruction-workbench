# requirement.md

**Project Owner / Signature:** Jerome_Yuxuan_Zhang  
**Project Type:** VSCode + GitHub 全栈工程项目需求文档  
**Primary Goal:** 构建一个面向学术/教学场景的 PPT 内容高保真提取与讲义生成系统  

---

## 1. 项目背景与目标

本项目旨在实现一个可在 VSCode 中开发、可托管于 GitHub、可由 AI Coding Agent（如 Codex / Claude Code）协助维护的工程系统，用于完成以下两类核心任务：

### 1.1 核心任务 A：PPT → Word 高保真重构

将用户提供的 PPT / PPTX 文件解析为具有较强结构保持能力、阅读逻辑完整、版式尽量无损的 Word 文档（DOCX）。这里的“提取”不是简单抽文字，而是要尽可能保留和重建：

- 标题层级
- 正文段落
- 项目符号与编号
- 表格
- 图片
- 图形
- SmartArt 的可还原部分
- 文本框布局关系
- 页面内阅读顺序
- 图文对应关系
- 页眉页脚、页码、备注（如有需要可配置）

输出 Word 文档的默认格式要求：

- 正文字号：12 pt
- 行距：单倍行距
- 英文字体：Times New Roman
- 中文字体：Noto Serif SC
- 默认段前段后：可配置，但初始建议为 0 pt / 0 pt
- 页面：A4，标准页边距

系统目标不是“逐对象机械导出”，而是“在语义逻辑与视觉信息之间取得平衡，生成适合继续编辑、整理、打印、归档的 Word 文档”。

### 1.2 核心任务 B：讲义制作 AI 工作流支持

提供一份可供 VSCode + Codex / Claude Code / 其他 AI Bot 加载的 Markdown 规范文档，用于指导 AI 根据课件、讲义、题目文件等材料，生成符合严格学术规范的 HTML 讲义。

该部分需要：

- 支持通过 AI Bot 学习“讲义制作规范”
- 支持将该规范作为 prompt / system-style reference / project memory 使用
- 支持未来接入 API 大模型，对内容进行自动整理或半自动整理
- 若检测到用户已配置 API Key，应提示是否启用 API 模式进行大模型整理

---

## 2. 项目总原则

### 2.1 工程原则

本项目必须遵循以下原则：

1. **可维护性优先**：代码结构清晰，模块边界明确，方便后续扩展。
2. **结果可审计**：对每一步提取与重构，尽可能保留日志、元数据与中间产物。
3. **高保真优先于速度**：在合理性能范围内，优先保证内容完整性与结构恢复质量。
4. **AI 能接手但不能失控**：所有供 AI 使用的规范必须清晰、可验证、可落地。
5. **接口优先设计**：讲义整理能力未来应可切换为本地规则、混合规则、API 大模型模式。
6. **默认离线可用**：在不依赖外部 API 的情况下，至少能完成 PPT → Word 的本地流程。
7. **跨语言兼容**：需充分考虑中英混排场景，避免中文乱码、英文字体错配、表格错位等问题。

### 2.2 非目标（Out of Scope）

第一阶段暂不要求：

- 完美还原所有动画效果
- 精准还原 PPT 中所有自由曲线与复杂矢量路径编辑语义
- 完整支持 VBA 宏
- 云端多人协作编辑
- 浏览器端在线编辑器
- 移动端适配

---

## 3. 用户场景

### 3.1 场景一：学生整理老师 PPT

用户上传课程 PPT，希望系统输出一份格式工整、逻辑清晰、可继续修改的 Word 讲义初稿。

### 3.2 场景二：研究者制作复习讲义

用户上传 PPT、PDF、Excel、习题文件，希望 AI Bot 在 VSCode 中依据既定规范生成闭环式 HTML 讲义。

### 3.3 场景三：半自动工作流

用户先用本地程序完成 PPT 内容抽取，再选择：

- 直接导出 Word
- 再调用本地 AI / API 大模型进行内容重组
- 生成 HTML 讲义
- 生成审校报告

---

## 4. 推荐技术栈

以下为建议，不要求完全一致，但最终方案必须满足需求与可维护性。

### 4.1 后端 / 核心处理

推荐语言：Python 3.11+

推荐库（可替换，但需说明理由）：

- `python-pptx`：解析 PPTX 基础对象
- `lxml`：必要时深入处理 Office Open XML
- `Pillow`：图片处理
- `python-docx`：生成 Word 文档
- `docxcompose` 或等效工具：复杂 DOCX 拼接增强
- `pydantic`：数据模型定义与校验
- `typer` 或 `click`：CLI 工具接口
- `fastapi`：提供 API 服务（可选但推荐）
- `uvicorn`：本地服务运行
- `jinja2`：模板生成（若需要 HTML / Markdown 模板）

### 4.2 前端 / 可选界面

若提供轻量界面，可选：

- FastAPI + Jinja2 模板页
- 或 Electron / Tauri（不强制）

第一阶段不强制 GUI，但建议至少有 CLI + API。

### 4.3 工程工具

- VSCode
- GitHub
- `pytest`
- `ruff`
- `black`
- `mypy`（可选但推荐）
- `pre-commit`
- `dotenv`

---

## 5. 系统模块设计

项目建议至少拆分为以下模块。

### 5.1 文件输入模块

负责：

- 读取 PPT / PPTX 文件
- 校验文件格式
- 建立任务目录
- 提取基础元信息（页数、尺寸、主题信息、作者等，能取则取）

### 5.2 PPT 解析模块

负责：

- 遍历每一页 slide
- 识别 shape 类型
- 区分：文本框、标题框、图片、表格、图形、组合对象、备注
- 获取位置信息、层级关系、尺寸信息、文本样式信息
- 建立 slide 内阅读顺序

### 5.3 语义重建模块

负责：

- 将 PPT 中碎片化对象整理成“阅读块”
- 判断标题层级
- 识别正文与注释
- 判断图文对应关系
- 判断表格标题、表格内容、图例、说明文字之间的联系
- 输出统一中间表示（IR, Intermediate Representation）

### 5.4 资源提取模块

负责：

- 导出图片
- 导出表格数据
- 提取可用图形信息
- 对无法直接保真重建的图形生成降级表示
- 记录丢失风险

### 5.5 Word 生成模块

负责：

- 基于统一中间表示生成 DOCX
- 设置默认字体、字号、行距、段落样式
- 插入图片
- 重建表格
- 适当处理分页与标题层级
- 输出最终 `.docx`

### 5.6 讲义规范模块

负责：

- 存储 AI 讲义生成规范 Markdown
- 提供给 AI Bot 使用的 instruction 模板
- 可扩展为 prompt builder
- 支持从本地模板中加载系统规范

### 5.7 API 服务模块

负责：

- 暴露任务接口
- 文件上传接口
- 任务状态接口
- 文档导出接口
- 可选：大模型整理接口

### 5.8 日志与审计模块

负责：

- 记录处理过程
- 记录每页提取对象统计
- 记录失败对象
- 输出 QA / report 文件

---

## 6. PPT → Word 功能需求（必须实现）

### 6.1 输入支持

必须支持：

- `.pptx`

可选支持：

- `.ppt`（可通过调用 LibreOffice 或其他转换工具先转为 `.pptx`）

### 6.2 文本提取要求

必须支持：

- 标题文本提取
- 普通段落提取
- 列表提取
- 多文本框阅读顺序重建
- 中英文字体保留到合理程度
- 粗体、斜体、下划线、颜色等基础样式尽量保留
- 上标、下标、特殊符号尽量保留

### 6.3 表格提取要求

必须支持：

- 表格单元格内容提取
- 行列结构重建
- 合并单元格尽量保留
- 表格标题与说明关联
- 导出到 Word 时保持尽量接近原逻辑

### 6.4 图片提取要求

必须支持：

- 将 PPT 中图片导出为独立资源
- 按原页逻辑插入 Word
- 尽量保留相对位置语义
- 图片下方如存在 caption，应关联输出

### 6.5 图形 / 形状处理要求

必须支持尽力处理以下对象：

- 普通矩形、圆形、箭头等基础 shape
- 结构图中的文本 + 连接关系
- SmartArt 的文本内容及层级
- 组合对象的拆解与重构

对于无法无损还原的复杂图形，应提供降级策略，例如：

- 导出为图片插入 Word
- 或转为“图形说明块”
- 并在日志中标注为“图形降级处理”

### 6.6 阅读逻辑重建

这是本项目的关键能力，不能只按 XML 顺序导出。

必须尽量实现：

- 基于坐标的版面排序
- 结合字体大小判断标题层级
- 识别左右分栏 / 上下结构
- 避免将图片说明与正文打乱
- 避免把页脚/装饰元素混入正文

建议输出中间层结构，例如：

- SlideDocument
- ContentBlock
- ParagraphBlock
- TableBlock
- FigureBlock
- ShapeDiagramBlock
- NotesBlock

### 6.7 Word 输出格式

默认要求：

- 页面：A4
- 页边距：Normal
- 正文字体：Times New Roman + Noto Serif SC
- 字号：12 pt
- 行距：single
- 标题层级有明确样式
- 图片居中或按语义布局处理
- 表格自动适配页宽

需要考虑：

- 中文字体优先 `Noto Serif SC`
- 英文字体优先 `Times New Roman`
- 对于 Word 中中英混排字体控制，可研究 run-level 设置策略

---

## 7. 中间表示（IR）设计要求

为了保证可维护性与未来扩展，必须先构建统一中间表示，而不是直接从 PPT 拼到 Word。

建议最少包含以下字段：

```text
Document
  ├── metadata
  ├── slides[]
Slide
  ├── slide_index
  ├── title
  ├── blocks[]
Block
  ├── block_id
  ├── block_type
  ├── bbox
  ├── z_index
  ├── semantic_role
  ├── content
  ├── style
  ├── relations
```

其中：

- `block_type` 可包括 text / table / image / diagram / notes / footer 等
- `semantic_role` 可包括 title / subtitle / body / caption / appendix / decorative 等
- `relations` 用于描述 caption-for、belongs-to、next-to、part-of 等关系

---

## 8. API 预留与 AI 整理能力

系统需要预留 API 模式，方便后续接入 OpenAI / Claude / Gemini / 本地模型。

### 8.1 API 模式目标

用于在“PPT 内容已提取完成”后，进一步实现：

- 内容结构优化
- 讲义重写
- HTML 讲义生成
- 复习提纲生成
- 习题重构与答案扩写

### 8.2 API 接入要求

应设计统一 LLM Provider 抽象层，例如：

- OpenAI provider
- Anthropic provider
- Gemini provider
- Local model provider

### 8.3 API 触发策略

当检测到以下条件时，系统可以提示用户：

- 已发现 `.env` 中存在 API Key
- 已配置模型提供商
- 用户在命令中启用了 `--use-llm` 或等效参数

提示文案建议类似：

> 检测到可用 API 模型配置。是否启用大模型对已提取内容进行进一步整理与讲义生成？

### 8.4 API 相关注意事项

必须说明：

- API 模式是可选增强，不是基础流程前置条件
- 使用 API 可能产生费用
- 敏感文件上传前应提醒用户注意隐私与合规

---

## 9. 讲义制作规范文档需求（必须提供）

项目中必须包含一个专门用于 AI Bot 学习的 Markdown 文档，例如：

- `docs/lecture_note_generation_spec.md`
- 或 `prompts/academic_lecture_reconstruction.md`

该文档应作为可加载的项目规范文件，供 VSCode 中的 Codex / Claude Code / 其他 AI 工具读取和参考。

此规范文档的内容必须整合用户提供的“严格学术讲义重构规范”，核心要求包括但不限于：

### 9.1 总目标

AI 不是做摘要，而是做：

- 完整迁移
- 完整解释
- 完整补全
- 形成闭环、自洽、可打印、可替代原材料的 HTML 讲义

### 9.2 闭环要求

必须迁移并解释源材料中的：

- 概念
- 定义
- 公式
- 定理
- 图表
- 例题
- 推导
- 比较
- 结论
- 题目与解答

不得写：

- “见原文”
- “略”
- “自行阅读”
- “see original”
- 或任何把理解责任推回源文件的话

### 9.3 补全规则

可做必要前置补全，但必须：

- 范围收敛
- 明确标注为“必要前置补全”
- 不能喧宾夺主
- 不能脱离用户文件乱扩展

### 9.4 语言规则

讲义应：

- 以中文为主
- 首次出现关键术语时附简洁英文
- 不做逐行双语翻译
- 不写成纯中文无英文术语支持的版本

### 9.5 HTML 输出规则

主产物必须：

- 恰好是一份完整 HTML
- 放在一个代码块中
- 可直接另存为 `.html`
- 内嵌 CSS
- 支持打印
- 数学公式使用 LaTeX
- 可使用 MathJax CDN
- 不要浮动目录、浮动按钮、sticky 元素

### 9.6 HTML 结构要求

必须包含：

1. 10 分钟速记区  
2. 全理论闭环重构  
3. 必要前置补全  
4. 图示重构（使用内联 SVG）  
5. 绿色纸笔练习区  
6. 全部例题 / 题目完整解答  

### 9.7 数学规则

- 所有公式必须解释变量含义
- 源材料有推导时要逐步重构
- 源材料只给结论但理解依赖推导时，可做狭义必要补全

### 9.8 外部自检要求

HTML 代码块外部必须附带“自检 / 覆盖核对”，且不能放进 HTML 主体。

> 以上内容必须明确写入 AI 规范 Markdown 文档中。  
> 该部分规范来源于用户提供的附件内容，应纳入项目文档设计。 

---

## 10. CLI 设计建议

建议至少提供如下命令：

### 10.1 PPT 转 Word

```bash
python -m app.cli ppt2docx input.pptx --output output.docx
```

### 10.2 提取中间表示

```bash
python -m app.cli extract-ir input.pptx --output ./artifacts/
```

### 10.3 生成讲义规范模板

```bash
python -m app.cli init-lecture-spec
```

### 10.4 调用 API 进行讲义整理

```bash
python -m app.cli lecture-generate ./artifacts/slide_ir.json --use-llm --provider openai
```

### 10.5 质量检查

```bash
python -m app.cli qa-check ./artifacts/
```

---

## 11. API 设计建议

若实现 FastAPI，建议至少暴露如下接口：

### 11.1 文件上传

`POST /api/v1/files/upload`

### 11.2 创建 PPT 解析任务

`POST /api/v1/tasks/ppt-to-docx`

### 11.3 查询任务状态

`GET /api/v1/tasks/{task_id}`

### 11.4 下载结果文档

`GET /api/v1/tasks/{task_id}/download`

### 11.5 使用 LLM 整理讲义

`POST /api/v1/tasks/lecture-generate`

### 11.6 获取系统配置

`GET /api/v1/system/config`

---

## 12. 目录结构建议

```text
project-root/
├── app/
│   ├── cli.py
│   ├── config.py
│   ├── main.py
│   ├── models/
│   │   ├── ir_models.py
│   │   └── task_models.py
│   ├── parsers/
│   │   ├── ppt_parser.py
│   │   ├── text_parser.py
│   │   ├── table_parser.py
│   │   ├── image_parser.py
│   │   └── diagram_parser.py
│   ├── builders/
│   │   ├── ir_builder.py
│   │   ├── docx_builder.py
│   │   └── html_builder.py
│   ├── services/
│   │   ├── task_service.py
│   │   ├── export_service.py
│   │   ├── qa_service.py
│   │   └── llm_service.py
│   ├── api/
│   │   ├── routes_files.py
│   │   ├── routes_tasks.py
│   │   └── routes_llm.py
│   └── utils/
│       ├── layout.py
│       ├── fonts.py
│       ├── logging_utils.py
│       └── file_utils.py
├── docs/
│   ├── architecture.md
│   ├── lecture_note_generation_spec.md
│   ├── qa_rules.md
│   └── api_usage.md
├── prompts/
│   └── lecture_reconstruction_prompt.md
├── tests/
│   ├── test_parser.py
│   ├── test_ir.py
│   ├── test_docx_export.py
│   └── test_api.py
├── samples/
│   ├── sample_ppt/
│   └── expected_outputs/
├── artifacts/
├── .env.example
├── pyproject.toml
├── README.md
└── requirement.md
```

---

## 13. 质量要求与验收标准

### 13.1 PPT → Word 验收标准

至少满足以下标准：

1. 可以正确读取常规 `.pptx` 文件。
2. 每页主要文本内容不得大面积丢失。
3. 表格内容可读且结构基本正确。
4. 图片可导出并插入文档。
5. 标题与正文层级大致正确。
6. 输出文档默认格式满足：12 pt、单倍行距、Times New Roman + Noto Serif SC。
7. 对复杂图形即便不能完全重建，也必须有可解释的降级策略。
8. 生成日志中应说明提取失败或降级对象。

### 13.2 AI 讲义规范文档验收标准

至少满足以下标准：

1. 文档结构清楚，适合 AI Bot 直接读取。
2. 已纳入“闭环重构”要求。
3. 已纳入 HTML 输出结构要求。
4. 已纳入中英术语规则。
5. 已纳入 SVG 图示与绿色练习区要求。
6. 已纳入“自检 / 覆盖核对”要求。
7. 已说明可选 API 模式。

### 13.3 工程质量标准

- 关键模块具备单元测试
- 具备至少一个示例输入与示例输出
- README 可让新开发者快速启动
- 代码风格一致
- 异常处理清晰
- 配置项集中管理

---

## 14. 错误处理与降级策略

系统不能只在理想输入上工作，必须有明确异常策略。

### 14.1 解析失败

若某 slide 或 shape 解析失败：

- 不应导致整个任务直接崩溃
- 应记录失败对象
- 应尽量保留其他内容导出

### 14.2 复杂图形失败

若复杂图形无法重构：

- 优先转图片
- 再附加说明
- 同时写入日志

### 14.3 字体缺失

若本机无 `Noto Serif SC`：

- 给出警告
- 提供回退字体策略
- 在 README 中说明如何安装推荐字体

### 14.4 API 不可用

若 API Key 缺失或调用失败：

- 不影响本地基础功能
- 明确提示用户 API 模式不可用
- 保证离线模式继续执行

---

## 15. 配置设计建议

建议支持以下配置项：

- 默认字体
- 默认字号
- 默认行距
- 是否导出备注
- 是否导出页脚
- 图形降级策略
- 是否启用 LLM
- LLM provider
- model name
- API key 环境变量名
- 输出目录
- 日志级别

建议支持：

- `.env`
- `config.yaml`
- CLI 参数覆盖

---

## 16. README 需要包含的内容

项目 README 至少要包括：

1. 项目简介
2. 功能列表
3. 技术栈
4. 安装步骤
5. 本地运行方式
6. CLI 示例
7. API 示例
8. 字体说明
9. 常见问题
10. 未来路线图

---

## 17. 开发阶段建议

### Phase 1：最小可用版本（MVP）

完成：

- `.pptx` 解析
- 文本 / 图片 / 表格导出
- 基础阅读顺序重建
- DOCX 输出
- CLI 可用

### Phase 2：质量增强

完成：

- 图形降级策略
- 更好的标题识别
- 更好的表格恢复
- QA 报告
- 单元测试补强

### Phase 3：AI 讲义能力

完成：

- 讲义规范 Markdown
- Prompt 模板
- LLM provider 抽象层
- API 整理流程

### Phase 4：完整服务化

完成：

- FastAPI 服务
- 任务管理
- 文件上传与下载
- 可选轻量 Web 界面

---

## 18. 对 AI Coding Agent 的明确要求

在 VSCode + Codex / Claude Code 环境中执行本需求时，AI Coding Agent 必须遵守：

1. 先搭项目骨架，再逐模块实现。
2. 先定义 IR 数据结构，再写导出逻辑。
3. 不允许直接写成一个巨型脚本。
4. 每完成一个模块，补最小可运行测试。
5. 遇到 PPT 复杂对象时，优先做可解释降级，而不是静默丢弃。
6. 所有关键设计选择要写入文档。
7. 涉及 LLM / API 的功能必须与本地离线功能解耦。
8. 若检测到 API 可用，应提示用户是否启用，而不是强制调用。

---

## 19. 最终交付物要求

本项目最终至少应交付：

1. 可运行的源代码
2. `README.md`
3. 本文件 `requirement.md`
4. AI 讲义规范文件 `docs/lecture_note_generation_spec.md`
5. 至少一个示例 PPT 与对应输出 DOCX
6. 测试文件
7. 可选 API 接口实现

---

## 20. 特别说明：讲义规范来源

项目中的“讲义制作规范”部分，必须显式参考并吸收用户提供的附件要求，其核心精神是：

- 不是摘要，而是闭环重构
- 不是省略，而是完整迁移
- 不是只抽文字，而是重建逻辑、结构、图示、例题与练习
- 输出必须可打印、可复习、可替代原始材料

开发者在实现 `docs/lecture_note_generation_spec.md` 时，必须充分吸收上述规则，不得写成空泛、简略、不可执行的模板。

---

## 21. 建议补充文件

建议额外生成以下文件：

- `docs/architecture.md`：说明架构与模块关系
- `docs/qa_rules.md`：定义提取质量检查规则
- `docs/api_usage.md`：说明 API 使用方法
- `prompts/lecture_reconstruction_prompt.md`：给 AI Bot 的 prompt 模板
- `samples/expected_outputs/`：存放理想输出示例

---

## 22. 一句话总结给执行代理

请在 VSCode 中基于本需求搭建一个可维护、可扩展、可审计的 GitHub 项目：先完成 PPT → Word 的高保真结构化提取，再补齐 AI 讲义生成规范与 API 预留能力，确保本地离线可用，同时支持未来调用大模型进行讲义整理。

---

**Signature:** Jerome_Yuxuan_Zhang
