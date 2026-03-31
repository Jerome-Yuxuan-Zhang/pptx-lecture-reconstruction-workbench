from __future__ import annotations

from dataclasses import dataclass

from app.builders.html_builder import HTMLBuilder
from app.config import AppConfig
from app.models.ir_models import SlideIRDocument


@dataclass(slots=True)
class LLMAvailability:
    configured: bool
    provider: str
    model: str
    message: str


class LLMService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.html_builder = HTMLBuilder()

    def availability(self) -> LLMAvailability:
        configured = self.config.has_llm_credentials
        if configured:
            message = (
                f"Detected API credentials for provider '{self.config.llm_provider}'. "
                "LLM mode is optional and may incur external API cost."
            )
        else:
            message = (
                "No LLM credentials detected. Falling back to offline generation. "
                "For full closed-loop lecture authoring, use the Codex workfile in docs/."
            )
        return LLMAvailability(
            configured=configured,
            provider=self.config.llm_provider,
            model=self.config.llm_model,
            message=message,
        )

    def generate_lecture_html(
        self, document_ir: SlideIRDocument, use_llm: bool = False
    ) -> tuple[str, str]:
        availability = self.availability()
        html = self.html_builder.build(document_ir)
        if use_llm and availability.configured:
            note = (
                "LLM provider is configured, but this repo keeps generation offline-first by default. "
                "Add a concrete provider adapter here when you want to call external APIs."
            )
        elif use_llm and not availability.configured:
            note = "Requested LLM mode, but no API key was found. Offline HTML draft generated instead."
        else:
            note = availability.message
        return html, note
