"""
CloudCart AI agent wrapper.

This module exposes a safe request handler that validates input/output,
reuses compiled prompts and Gemini chains, and caches repeated queries.
"""

import pathlib
import re
from functools import lru_cache
from typing import Any

import yaml
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from app.config.settings import settings
from app.tools.cloudcart_tools import (
    _calculate_shipping_cost,
    _check_product_availability,
    _get_order_status,
)
from app.utils.security import is_simple_small_talk, small_talk_response
from app.validators.input_validator import CloudCartInput
from app.validators.output_validator import CloudCartOutput


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
            raise RuntimeError("GOOGLE_API_KEY is not set. Cannot invoke the PromptManager.")
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
                "Gemini quota exceeded for this API key / project. "
                "Please wait for quota reset or use a key with available quota."
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

    @property
    def current_version(self) -> str:
        return self._spec.get("persona", {}).get("policy_version", "unknown")

    def _compile(self) -> None:
        persona = self._spec["persona"]
        task = self._spec.get("task", {})
        templates = self._spec["templates"]
        security = self._spec.get("security", {})

        few_shot_examples = task.get("few_shot_examples", [])
        few_shot_block = "\n".join(
            f"User: {ex['user']}\nAssistant: {ex['assistant']}"
            for ex in few_shot_examples
        )

        system_text = templates["system"].format(
            persona_role=persona["role"],
            persona_platform=persona["platform"],
            policy_version=persona["policy_version"],
            tone=persona["tone"],
            off_topic_response=security.get("off_topic_response", ""),
            few_shot_block=few_shot_block,
        )

        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_text),
                ("human", templates["human"]),
            ]
        )


ORDER_ID_PATTERN = re.compile(r"\bCC[- ]?\d{5}\b", re.I)
PRODUCT_NAMES = [
    "wireless headphones",
    "fitness tracker",
    "smartphone case",
    "laptop sleeve",
    "usb-c hub",
]
WEIGHT_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)\b", re.I)
DESTINATION_PATTERN = re.compile(r"\b(?:to|in|for)\s+([A-Za-z ]+?)(?:\?|\.|$)", re.I)


def _extract_order_id(text: str) -> str | None:
    match = ORDER_ID_PATTERN.search(text)
    if not match:
        return None
    return match.group(0).replace(" ", "-").upper()


def _extract_product_name(text: str) -> str | None:
    text_lower = text.lower()
    for product_name in PRODUCT_NAMES:
        if product_name in text_lower:
            return product_name
    return None


def _parse_shipping_query(text: str) -> dict[str, Any] | None:
    weight_match = WEIGHT_PATTERN.search(text)
    destination_match = DESTINATION_PATTERN.search(text)
    if not weight_match or not destination_match:
        return None

    return {
        "weight_kg": float(weight_match.group(1)),
        "destination": destination_match.group(1).strip(),
        "express": bool(re.search(r"\b(express|fast|priority|overnight)\b", text, re.I)),
    }


def _route_local_query(user_query: str) -> str | None:
    order_id = _extract_order_id(user_query)
    if order_id and re.search(r"\b(order|status|track|tracking|shipment)\b", user_query, re.I):
        return _get_order_status(order_id)

    product_name = _extract_product_name(user_query)
    if product_name and re.search(r"\b(available|stock|in stock|out of stock|inventory)\b", user_query, re.I):
        return _check_product_availability(product_name)

    shipping_payload = _parse_shipping_query(user_query)
    if shipping_payload:
        shipping_result = _calculate_shipping_cost(**shipping_payload)
        express_text = " with express shipping" if shipping_result["express"] else ""
        return (
            f"Shipping to {shipping_result['destination']} costs ${shipping_result['cost_usd']} "
            f"and takes approximately {shipping_result['shipping_days']} days{express_text}."
        )

    return None


_PROMPT_MANAGER: PromptManager | None = None


def get_prompt_manager() -> PromptManager:
    global _PROMPT_MANAGER
    if _PROMPT_MANAGER is None:
        _PROMPT_MANAGER = PromptManager()
    return _PROMPT_MANAGER


def safe_cloudcart_agent(user_query: str) -> dict[str, Any]:
    if not settings.GOOGLE_API_KEY:
        return {
            "success": False,
            "error_code": "MISSING_API_KEY",
            "message": "GOOGLE_API_KEY is not set. Cannot invoke the Gemini API.",
        }

    try:
        normalized_query = user_query.strip()
        if settings.ENABLE_INPUT_VALIDATION:
            validated = CloudCartInput(user_query=user_query)
            normalized_query = validated.user_query

        if is_simple_small_talk(normalized_query):
            response_text = small_talk_response(normalized_query)
        else:
            local_response = _route_local_query(normalized_query)
            if local_response is not None:
                response_text = local_response
            else:
                response_text = get_prompt_manager().invoke(normalized_query)

        if settings.ENABLE_OUTPUT_VALIDATION:
            CloudCartOutput(response=response_text)

        return {
            "success": True,
            "error_code": None,
            "response": response_text,
        }
    except ValidationError as exc:
        return {
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": str(exc),
        }
    except Exception as exc:
        return {
            "success": False,
            "error_code": "LLM_ERROR",
            "message": str(exc),
        }
