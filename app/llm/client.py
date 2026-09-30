from langchain_openai import ChatOpenAI

from app.config import settings


def get_llm() -> ChatOpenAI:
    """Create the shared LLM client used for planning and synthesis."""

    if not settings.nvidia_api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not configured."
        )

    return ChatOpenAI(
        model=settings.nvidia_model,
        base_url=settings.nvidia_base_url,
        api_key=settings.nvidia_api_key,
        temperature=0,
    )