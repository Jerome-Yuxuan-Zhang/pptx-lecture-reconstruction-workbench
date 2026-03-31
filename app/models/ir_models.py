from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

BlockType = Literal["text", "table", "image", "diagram", "notes", "footer"]
SemanticRole = Literal[
    "title",
    "subtitle",
    "body",
    "caption",
    "appendix",
    "decorative",
    "notes",
    "footer",
]


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def center_x(self) -> float:
        return self.x + (self.width / 2)

    @property
    def center_y(self) -> float:
        return self.y + (self.height / 2)


class TextRun(BaseModel):
    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: str | None = None
    font_size_pt: float | None = None
    font_name: str | None = None
    level: int = 0
    superscript: bool = False
    subscript: bool = False


class TableCellContent(BaseModel):
    row: int
    col: int
    text: str
    row_span: int = 1
    col_span: int = 1


class BlockRelation(BaseModel):
    relation_type: str
    target_block_id: str
    score: float = 1.0


class BlockStyle(BaseModel):
    font_size_pt: float | None = None
    font_name: str | None = None
    color: str | None = None
    alignment: str | None = None
    bullet: bool = False
    level: int = 0
    is_placeholder_title: bool = False
    shape_type: str | None = None


class ContentBlock(BaseModel):
    block_id: str
    block_type: BlockType
    bbox: BoundingBox
    z_index: int = 0
    semantic_role: SemanticRole = "body"
    content: dict[str, Any] = Field(default_factory=dict)
    style: BlockStyle = Field(default_factory=BlockStyle)
    relations: list[BlockRelation] = Field(default_factory=list)
    source_shape_name: str | None = None
    warnings: list[str] = Field(default_factory=list)


class SlideDocument(BaseModel):
    slide_index: int
    title: str | None = None
    notes: str | None = None
    blocks: list[ContentBlock] = Field(default_factory=list)
    width_pt: float | None = None
    height_pt: float | None = None


class DocumentMetadata(BaseModel):
    source_path: str
    source_name: str
    slide_count: int
    slide_width_pt: float
    slide_height_pt: float
    author: str | None = None
    company: str | None = None
    language_hint: str = "zh-CN,en"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    extractor_version: str = "0.1.0"


class SlideIRDocument(BaseModel):
    metadata: DocumentMetadata
    slides: list[SlideDocument] = Field(default_factory=list)
