from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
from .templates import build_safe_prompt


def create_llm_chain():
    prompt = build_safe_prompt().partial(
        platform="CloudCart v4.2",
        policy_version="2025-Q2"
    )

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=settings.GEMINI_TEMPERATURE,
        google_api_key=settings.GOOGLE_API_KEY,
    )

    return prompt | llm