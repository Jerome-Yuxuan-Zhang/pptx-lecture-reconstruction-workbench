# Codex 无损编译工作单

把这个文件和 `docs/lossless_course_material_compiler_spec.md` 一起交给 VSCode 里的 Codex。你只需要先改路径，然后对 Codex 说：

`请严格按照本工作单和 docs/lossless_course_material_compiler_spec.md，直接完成无损课程材料编译，不要先做总结。`

## 1. 本次批次信息

- 批次编号：
  `batch-001`
- 课程名：
  `请填写课程名`
- 周次 / Lecture / Topic：
  `请填写本批次范围`
- 本次处理目标：
  `先做无损底稿，不进入讲义解释层`

## 2. 输入材料

- 原始课件：
  `samples/sample_ppt/demo_course.pptx`
- 提取后的 IR：
  `samples/expected_outputs/demo_course/slide_ir.json`
- QA 报告：
  `samples/expected_outputs/demo_course/qa_report.md`
- 图形降级资产：
  `samples/expected_outputs/demo_course/assets/`
- 额外补充材料：
  `请在这里补充 PDF / 习题 / OCR / 录音转写路径`

## 3. 输出文件

- Source Register：
  `artifacts/material_compiler/batch-001/source_register.md`
- Lossless Compilation：
  `artifacts/material_compiler/batch-001/lossless_compilation.md`
- Concept Index：
  `artifacts/material_compiler/batch-001/concept_index.md`
- Dependency Map：
  `artifacts/material_compiler/batch-001/dependency_map.md`
- Ambiguity & Risk Log：
  `artifacts/material_compiler/batch-001/ambiguity_risk_log.md`
- No-loss Audit Checklist：
  `artifacts/material_compiler/batch-001/no_loss_audit.md`
- Continuation State：
  `artifacts/material_compiler/batch-001/continuation_state.md`

## 4. 执行约束

1. 不得删减。
2. 不得压缩。
3. 不得把整理做成总结。
4. 不得把解释层伪装成原文层。
5. 若材料太长，必须输出连续续传状态。
6. 若有 OCR 或图像问题，必须记录在风险日志中。
7. 若有图示信息，必须逐元素保留，不得只写“图略”。

## 5. 输出顺序

请严格按下列顺序执行：

1. Source Register
2. Lossless Transcription
3. Structured Reorganization
4. Concept Index
5. Dependency Map
6. Ambiguity & Risk Log
7. No-loss Audit Checklist
8. Continuation Protocol

## 6. 交付格式

请最终完成两件事：

1. 把以上各文件写到指定路径
2. 在聊天里简短汇报：
   - 这批处理到哪里
   - 发现了哪些高风险缺口
   - 下一批应从哪里接续
