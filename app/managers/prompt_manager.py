import pathlib
from functools import lru_cache
from typing import Any

import yaml
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.settings import settings


class PromptManager:
    """Loads a versioned YAML prompt spec and keeps a reusable Gemini chain."""

    def __init__(self, yaml_path: str | None = None):
        configured_path = yaml_path or f"{settings.PROMPT_DIR}/{settings.CURRENT_PROMPT_FILE}"
        self.yaml_path = pathlib.Path(configured_path)
        self._spec: dict = {}
        self._prompt: ChatPromptTemplate | None = None
        self._model_chains: list[tuple[str, Any]] = []
        self.load()

    def load(self, yaml_path: str | None = None) -> None:
        if yaml_path:
            self.yaml_path = pathlib.Path(yaml_path)

        with open(self.yaml_path, encoding="utf-8") as f:
            self._spec = yaml.safe_load(f) or {}

        self._compile()
        self._prepare_model_chains()
        self._get_response.cache_clear()

    def invoke(self, user_query: str) -> str:
        if not settings.GOOGLE_API_KEY:
            raise RuntimeError("Missing GOOGLE_API_KEY in environment.")
        if self._prompt is None:
            self.load()

        if settings.ENABLE_RESPONSE_CACHE:
            return self._get_response(user_query)
        return self._get_response_uncached(user_query)

    @lru_cache(maxsize=settings.RESPONSE_CACHE_SIZE)
    def _get_response(self, user_query: str) -> str:
        return self._generate_response(user_query)

    def _get_response_uncached(self, user_query: str) -> str:
        return self._generate_response(user_query)

    def _generate_response(self, user_query: str) -> str:
        last_error: Exception | None = None
        if not self._model_chains:
            self._prepare_model_chains()

        for model_name, chain in self._model_chains:
            try:
                response = chain.invoke({"user_query": user_query})
                return response.content
            except Exception as exc:
                last_error = exc
                continue

        error_text = str(last_error) if last_error else "Unknown Gemini error."
        if "RESOURCE_EXHAUSTED" in error_text or "quota" in error_text.lower():
            return (
                "Gemini quota exceeded for this API key/project. "
                "Please use a key/project with available free quota or wait for quota reset."
            )

        return f"All configured Gemini models failed. Last error: {error_text}"

    def _prepare_model_chains(self) -> None:
        self._model_chains = []
        model_names = [settings.GEMINI_MODEL] + [
            fallback
            for fallback in settings.GEMINI_MODEL_FALLBACKS
            if fallback and fallback != settings.GEMINI_MODEL
        ]

        for model_name in model_names:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=settings.GEMINI_TEMPERATURE,
                google_api_key=settings.GOOGLE_API_KEY,
            )
            self._model_chains.append((model_name, self._prompt | llm))
