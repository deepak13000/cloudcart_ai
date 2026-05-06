import yaml
import pathlib
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.settings import settings


class PromptManager:

    def __init__(self, yaml_path: str | None = None):
        configured_path = yaml_path or f"{settings.PROMPT_DIR}/{settings.CURRENT_PROMPT_FILE}"
        self.yaml_path = pathlib.Path(configured_path)
        self._spec = None
        self._prompt = None
        self._llm = None

        self.load()

    def load(self):
        with open(self.yaml_path) as f:
            self._spec = yaml.safe_load(f)

        self._compile()

    def _compile(self):
        persona = self._spec["persona"]
        task = self._spec.get("task", {})
        templates = self._spec["templates"]
        few_shot_examples = task.get("few_shot_examples", [])

        few_shot_block = "\n".join(
            [f'User: {example["user"]}\nAssistant: {example["assistant"]}' for example in few_shot_examples]
        )

        system_text = templates["system"].format(
            persona_role=persona["role"],
            persona_platform=persona["platform"],
            policy_version=persona["policy_version"],
            tone=persona["tone"],
            off_topic_response=self._spec["security"]["off_topic_response"],
            few_shot_block=few_shot_block
        )

        self._prompt = ChatPromptTemplate.from_messages([
            ("system", system_text),
            ("human", templates["human"])
        ])

    def invoke(self, user_query: str):
        if not settings.GOOGLE_API_KEY:
            raise RuntimeError("Missing GOOGLE_API_KEY in environment.")
        try:
            models_to_try = [settings.GEMINI_MODEL] + [
                model for model in settings.GEMINI_MODEL_FALLBACKS if model != settings.GEMINI_MODEL
            ]
            last_error = None
            for model_name in models_to_try:
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        temperature=settings.GEMINI_TEMPERATURE,
                        google_api_key=settings.GOOGLE_API_KEY,
                    )
                    chain = self._prompt | llm
                    response = chain.invoke({"user_query": user_query})
                    return response.content
                except Exception as exc:
                    last_error = exc

            error_text = str(last_error) if last_error else "Unknown Gemini error."
            if "RESOURCE_EXHAUSTED" in error_text or "quota" in error_text.lower():
                return (
                    "Gemini quota exceeded for this API key/project. "
                    "Please use a key/project with available free quota or wait for quota reset."
                )

            return (
                "All configured Gemini models failed. "
                f"Last error: {error_text}"
            )
        except Exception as exc:
            return (
                "Sorry, I am unable to process your request right now. "
                f"Details: {exc}"
            )