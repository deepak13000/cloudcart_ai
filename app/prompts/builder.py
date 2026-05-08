"""
Part A — LLM chain builder.

Demonstrates using ChatPromptTemplate.partial() to lock in static context
(platform, policy_version) so the user_query path can never override them.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from app.chains.templates import build_safe_prompt
from app.config.settings import settings


def create_llm_chain():
    """
    Build and return a runnable chain:  prompt | llm

    Static variables are baked in via .partial(); only {user_query} remains
    as a live placeholder for the caller to supply at invoke-time.
    """

    # .partial() locks platform / policy_version — they cannot be overridden
    # by anything in the user_query path.
    prompt = build_safe_prompt().partial(
        platform="CloudCart v4.2",
        policy_version="2025-Q2",
    )

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=settings.GEMINI_TEMPERATURE,
        google_api_key=settings.GOOGLE_API_KEY,
    )

    # LangChain LCEL pipe — prompt feeds into llm automatically
    return prompt | llm