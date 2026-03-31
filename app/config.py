from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    output_dir: Path = Field(default=Path("artifacts"))
    log_level: str = Field(default="INFO")
    default_body_font: str = Field(default="Times New Roman")
    default_cjk_font: str = Field(default="Noto Serif SC")
    fallback_cjk_font: str = Field(default="SimSun")
    default_font_size_pt: float = Field(default=12.0)
    default_line_spacing: float = Field(default=1.0)
    export_notes: bool = Field(default=False)
    export_footer: bool = Field(default=False)
    diagram_fallback: str = Field(default="svg+preview")
    enable_llm: bool = Field(default=False)
    llm_provider: str = Field(default="openai")
    llm_model: str = Field(default="gpt-4o-mini")
    llm_api_key_env: str = Field(default="OPENAI_API_KEY")
    lecture_spec_path: Path = Field(default=Path("docs/lecture_note_generation_spec.md"))

    @property
    def llm_api_key(self) -> str | None:
        import os

        return os.getenv(self.llm_api_key_env)

    @property
    def has_llm_credentials(self) -> bool:
        return bool(self.llm_api_key)


def _read_yaml(config_path: Path | None) -> dict[str, Any]:
    if not config_path or not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("config.yaml must contain a mapping at the top level")
    return data


def _normalize_path_fields(config: AppConfig) -> AppConfig:
    data = config.model_dump()
    for key in ("output_dir", "lecture_spec_path"):
        data[key] = Path(data[key])
    return AppConfig.model_validate(data)


def load_config(
    config_path: Path | None = None, overrides: dict[str, Any] | None = None
) -> AppConfig:
    import os

    load_dotenv()
    yaml_data = _read_yaml(config_path)
    env_data = {
        "output_dir": os.getenv("PPTX2DOCX_OUTPUT_DIR"),
        "log_level": os.getenv("PPTX2DOCX_LOG_LEVEL"),
        "default_body_font": os.getenv("PPTX2DOCX_DEFAULT_BODY_FONT"),
        "default_cjk_font": os.getenv("PPTX2DOCX_DEFAULT_CJK_FONT"),
        "fallback_cjk_font": os.getenv("PPTX2DOCX_FALLBACK_CJK_FONT"),
        "default_font_size_pt": os.getenv("PPTX2DOCX_DEFAULT_FONT_SIZE_PT"),
        "default_line_spacing": os.getenv("PPTX2DOCX_DEFAULT_LINE_SPACING"),
        "export_notes": os.getenv("PPTX2DOCX_EXPORT_NOTES"),
        "export_footer": os.getenv("PPTX2DOCX_EXPORT_FOOTER"),
        "diagram_fallback": os.getenv("PPTX2DOCX_DIAGRAM_FALLBACK"),
        "enable_llm": os.getenv("PPTX2DOCX_ENABLE_LLM"),
        "llm_provider": os.getenv("PPTX2DOCX_LLM_PROVIDER"),
        "llm_model": os.getenv("PPTX2DOCX_LLM_MODEL"),
        "llm_api_key_env": os.getenv("PPTX2DOCX_LLM_API_KEY_ENV"),
    }
    payload = {
        **yaml_data,
        **{key: value for key, value in env_data.items() if value not in (None, "")},
        **(overrides or {}),
    }
    config = AppConfig.model_validate(payload)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    return _normalize_path_fields(config)


@lru_cache
def get_config() -> AppConfig:
    return load_config()
