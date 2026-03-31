from __future__ import annotations

import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.run import Run

_CJK_RE = re.compile(r"[\u3400-\u9fff]")


def contains_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(text))


def apply_run_fonts(run: Run, latin_font: str, cjk_font: str) -> None:
    run.font.name = latin_font
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:ascii"), latin_font)
    r_fonts.set(qn("w:hAnsi"), latin_font)
    r_fonts.set(qn("w:eastAsia"), cjk_font)
    r_fonts.set(qn("w:cs"), latin_font)
