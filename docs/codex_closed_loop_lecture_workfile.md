# Codex 闭环讲义工作单

建议先完成一次无损编译，再使用本工作单。

推荐先读：

- `docs/lossless_course_material_compiler_spec.md`
- `docs/codex_lossless_compilation_workfile.md`

然后再把这个文件和 `docs/lecture_note_generation_spec.md` 一起交给 VSCode 里的 Codex。

你可以直接对 Codex 说：

`请基于无损底稿、QA 报告和本工作单，严格按照 docs/lecture_note_generation_spec.md，完成闭环讲义重构。`

## 1. 本次输入

- 课件 PPTX：
  `samples/sample_ppt/demo_course.pptx`
- 提取后的 IR JSON：
  `samples/expected_outputs/demo_course/slide_ir.json`
- QA 报告：
  `samples/expected_outputs/demo_course/qa_report.md`
- 额外补充材料：
  `请在这里补充 PDF / 习题 / Excel / 参考答案路径`

## 2. 本次输出

- 目标 HTML：
  `artifacts/lecture_outputs/demo_course_closed_loop.html`
- 外部自检说明：
  `artifacts/lecture_outputs/demo_course_self_check.md`

## 3. 不可妥协的要求

1. 不是摘要，而是闭环重构。
2. 不得写“见原文”“略”“自行阅读”“see original”。
3. 讲义要覆盖概念、定义、公式、图示、例题、推导、比较、结论、题目与解答。
4. 如果必须补前置知识，只能做“必要前置补全”，并显式标注。
5. 图示优先改写为内联 SVG；若无法完整还原，至少把结构关系讲清楚。
6. 输出必须适合打印，且 HTML 只能有一个完整文档主体。
7. HTML 外必须附带“自检 / 覆盖核对”。

## 4. 你要按这个顺序执行

1. 读取 PPTX、IR、QA 和补充材料。
2. 列出本讲义必须覆盖的知识点，不得漏掉 slide 中出现的主内容。
3. 判断哪些部分需要“必要前置补全”，并保持范围收敛。
4. 重构完整理论链条、图示、例题与解答。
5. 输出一个完整 HTML 文件。
6. 另写一个外部自检文件，说明覆盖情况、补全点、缺失点和待人工确认点。

## 5. 输出质量下限

- 中文主述，首次术语附英文。
- 数学公式必须解释变量含义。
- 如果源材料有推导，就要逐步重构，不允许只抄结论。
- 如果存在图形降级资产，请优先读取：
  `samples/expected_outputs/demo_course/assets/`
- 如果 QA 报告里有降级块，必须在讲义里妥善吸收，不允许静默跳过。

## 6. 交付格式

请最终只做三件事：

1. 写出 HTML 文件到目标路径。
2. 写出外部自检文件到目标路径。
3. 在聊天里简短汇报：
   - 覆盖了哪些部分
   - 哪些地方做了必要前置补全
   - 哪些地方仍需人工确认
