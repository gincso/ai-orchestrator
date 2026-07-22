from openai import OpenAI
from config import settings

client = OpenAI(
    api_key=settings.openrouter_api_key or "sk-or-v1-placeholder",
    base_url=settings.openrouter_base_url,
)


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "",
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    model = model or settings.agent_model
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        extra_headers={
            "HTTP-Referer": "https://github.com/gincso/ai-orchestrator",
            "X-Title": "AI Orchestrator",
        },
    )
    return resp.choices[0].message.content or ""


def call_llm_with_tools(
    system_prompt: str,
    user_prompt: str,
    tools: list[dict],
    model: str = "",
    temperature: float = 0.3,
    max_tokens: int = 8192,
):
    model = model or settings.agent_model
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        tools=tools,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_headers={
            "HTTP-Referer": "https://github.com/gincso/ai-orchestrator",
            "X-Title": "AI Orchestrator",
        },
    )
    return resp.choices[0].message
