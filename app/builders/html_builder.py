from __future__ import annotations

from jinja2 import Template

from app.models.ir_models import SlideIRDocument

HTML_TEMPLATE = Template(
    """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{ title }}</title>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    :root {
      --page-width: 210mm;
      --accent: #1f6f50;
      --ink: #182028;
      --paper: #fbfaf4;
      --rule: #d7ddcf;
      --practice: #edf7eb;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(31,111,80,0.10), transparent 28rem),
        linear-gradient(180deg, #f5f3ea, #ffffff 18rem);
      font-family: "Source Han Serif SC", "Noto Serif SC", serif;
      line-height: 1.65;
    }
    main {
      max-width: var(--page-width);
      margin: 0 auto;
      padding: 18mm 16mm 24mm;
      background: var(--paper);
      min-height: 100vh;
    }
    h1, h2, h3 { margin: 0 0 0.5rem; color: #103825; }
    section { margin: 0 0 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--rule); }
    .panel { padding: 1rem 1.2rem; border: 1px solid var(--rule); border-radius: 14px; background: #fff; }
    .practice { background: var(--practice); border-color: #c1d9bf; }
    .slide { page-break-inside: avoid; }
    ul { margin: 0.5rem 0 0.75rem 1.2rem; }
    .muted { color: #56616a; font-size: 0.95rem; }
    @media print {
      body { background: #fff; }
      main { max-width: none; padding: 10mm 8mm 14mm; }
      section { break-inside: avoid; }
    }
  </style>
</head>
<body>
  <main>
    <section>
      <h1>{{ title }}</h1>
      <p class="muted">基于提取后的 PPT IR 自动生成的离线讲义草稿，可继续交由 AI 或人工精修。</p>
    </section>
    <section class="panel">
      <h2>10 分钟速记区</h2>
      <ul>
        {% for item in quick_notes %}
        <li>{{ item }}</li>
        {% endfor %}
      </ul>
    </section>
    <section>
      <h2>全理论闭环重构</h2>
      {% for slide in slides %}
      <article class="slide panel">
        <h3>{{ slide.title or ("Slide " ~ slide.slide_index) }}</h3>
        {% for paragraph in slide.paragraphs %}
        <p>{{ paragraph }}</p>
        {% endfor %}
      </article>
      {% endfor %}
    </section>
    <section class="panel">
      <h2>必要前置补全</h2>
      <p>必要前置补全：当前离线模式只依据 PPT 已提取信息组织内容；若源材料存在跳步推导、省略定义或公式变量未解释，建议后续启用人工或 LLM 精修。</p>
    </section>
    <section class="panel">
      <h2>图示重构</h2>
      <svg viewBox="0 0 800 180" width="100%" height="180" role="img" aria-label="流程示意图">
        <rect x="20" y="40" width="210" height="80" rx="18" fill="#e3f1e7" stroke="#1f6f50" stroke-width="2" />
        <rect x="295" y="40" width="210" height="80" rx="18" fill="#fff6d9" stroke="#ac7c1a" stroke-width="2" />
        <rect x="570" y="40" width="210" height="80" rx="18" fill="#e7eef8" stroke="#2f5c9b" stroke-width="2" />
        <text x="125" y="87" text-anchor="middle" font-size="24" fill="#103825">PPT 结构提取</text>
        <text x="400" y="87" text-anchor="middle" font-size="24" fill="#704d00">语义重建</text>
        <text x="675" y="87" text-anchor="middle" font-size="24" fill="#214571">讲义 / Word 输出</text>
        <line x1="230" y1="80" x2="295" y2="80" stroke="#54606a" stroke-width="3" />
        <line x1="505" y1="80" x2="570" y2="80" stroke="#54606a" stroke-width="3" />
      </svg>
      <p class="muted">若需忠实重建复杂图形，请基于原始形状信息进一步绘制细化 SVG。</p>
    </section>
    <section class="panel practice">
      <h2>绿色纸笔练习区</h2>
      <p>请根据本讲义自行补写：1) 关键定义；2) 公式变量释义；3) 一个自拟例题及其完整解答。</p>
    </section>
    <section class="panel">
      <h2>全部例题 / 题目完整解答</h2>
      <p>离线模式不会臆造题目答案。本节保留为后续精修入口，建议在接入题目源文件或启用 LLM 后补全。</p>
    </section>
  </main>
</body>
</html>
"""
)


class HTMLBuilder:
    def build(self, document_ir: SlideIRDocument) -> str:
        slides = []
        quick_notes: list[str] = []
        for slide in document_ir.slides:
            paragraphs = []
            for block in slide.blocks:
                text = (block.content.get("text") or "").strip()
                if block.semantic_role == "title" or not text:
                    continue
                paragraphs.extend(line for line in text.splitlines() if line.strip())
            if slide.title:
                quick_notes.append(slide.title)
            slides.append(
                {
                    "slide_index": slide.slide_index,
                    "title": slide.title,
                    "paragraphs": paragraphs[:8],
                }
            )
        return HTML_TEMPLATE.render(
            title=document_ir.metadata.source_name,
            slides=slides,
            quick_notes=quick_notes[:8] or ["请补充本节核心要点"],
        )
