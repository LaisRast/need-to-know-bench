from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    provider: str
    vendor: str
    model: str
    display_name: str
    created: str = ""

    @property
    def id(self) -> str:
        if self.vendor:
            return f"{self.provider}/{self.vendor}/{self.model}"
        return f"{self.provider}/{self.model}"


REGISTRY: list[Model] = [
    Model("openrouter", "amazon", "nova-2-lite-v1", "Nova 2 Lite", "2025-12-02"),
    Model("openrouter", "anthropic", "claude-opus-5.5", "Claude Opus 5.5", "2026-09-22"),
    Model("openrouter", "anthropic", "claude-sonnet-5.5", "Claude Sonnet 5.5", "2026-09-28"),
    Model("openrouter", "anthropic", "claude-haiku-5.5", "Claude Haiku 5.5", "2026-10-07"),
    Model("openrouter", "anthropic", "claude-fable-5.1", "Claude Fable 5.1", "2026-09-01"),
    Model(
        "openrouter",
        "deepseek",
        "deepseek-v4.1-flash-1017",
        "DeepSeek V4.1 Flash 1017",
        "2026-10-17",
    ),
    Model("openrouter", "deepseek", "deepseek-v4-pro-0813", "DeepSeek V4 Pro 0813", "2026-08-12"),
    Model("openrouter", "google", "gemini-4-argon", "Gemini 4 Argon", "2026-10-13"),
    Model("openrouter", "google", "gemini-3.8-flash", "Gemini 3.8 Flash", "2026-09-02"),
    Model("openrouter", "google", "gemma-4-31b-it", "Gemma 4 31B", "2026-04-02"),
    Model("openrouter", "meta", "muse-spark-1.3", "Muse Spark 1.3", "2026-09-02"),
    Model("openrouter", "meta-llama", "llama-4-maverick", "Llama 4 Maverick", "2025-04-05"),
    Model("openrouter", "meta-llama", "llama-4-scout", "Llama 4 Scout", "2025-04-05"),
    Model("openrouter", "minimax", "minimax-m3", "MiniMax M3", "2026-05-31"),
    Model("openrouter", "mistralai", "mistral-large-4-0", "Mistral Large 4", "2026-10-06"),
    Model("openrouter", "mistralai", "mistral-medium-3-5", "Mistral Medium 3.5", "2026-04-30"),
    Model("openrouter", "mistralai", "mistral-small-2603", "Mistral Small 4", "2026-03-16"),
    Model("openrouter", "moonshotai", "kimi-k3", "Kimi K3", "2026-07-16"),
    Model("openrouter", "nvidia", "nemotron-3-ultra-550b-a55b", "Nemotron 3 Ultra", "2026-06-04"),
    Model("openrouter", "openai", "gpt-oss-120b", "gpt-oss-120b", "2025-08-05"),
    Model("openrouter", "openai", "gpt-5.5", "GPT-5.5", "2026-04-24"),
    Model("openrouter", "openai", "gpt-5.6-terra", "GPT-5.6 Terra", "2026-07-09"),
    Model("openrouter", "openai", "gpt-6-luna", "GPT-6 Luna", "2026-09-22"),
    Model("openrouter", "openai", "gpt-6.1-sol", "GPT-6.1 Sol", "2026-09-29"),
    Model("openrouter", "openai", "gpt-6-astra", "GPT-6 Astra", "2026-09-04"),
    Model("openrouter", "stepfun", "step-5-preview", "Step 5 Preview", "2026-10-08"),
    Model("openrouter", "tencent", "hy3", "Hy3", "2026-07-06"),
    Model("openrouter", "tencent", "hy4-preview", "Hy4 preview", "2026-08-28"),
    Model("openrouter", "upstage", "solar-pro4", "Solar Pro 4", "2026-08-10"),
    Model("openrouter", "xiaomi", "mimo-v2.5", "MiMo-V2.5", "2026-04-22"),
    Model("openrouter", "xiaomi", "mimo-v2.6-flash", "MiMo-V2.6-Flash", "2026-09-21"),
    Model("openrouter", "x-ai", "grok-4.7", "Grok 4.7", "2026-09-21"),
    Model("openrouter", "qwen", "qwen3.8-27b", "Qwen3.8 27B", "2026-08-14"),
    Model("openrouter", "qwen", "qwen3.8-flash", "Qwen3.8 Flash", "2026-08-26"),
    Model("openrouter", "qwen", "qwen3.8-max-0902", "Qwen3.8 Max (0902)", "2026-09-03"),
    Model("openrouter", "z-ai", "glm-5.3", "GLM 5.3", "2026-08-18"),
    Model("openrouter", "z-ai", "glm-5.3-flash", "GLM 5.3 Flash", "2026-08-26"),
]

BY_ID: dict[str, Model] = {m.id: m for m in REGISTRY}


def lookup(model_id: str) -> Model:
    if m := BY_ID.get(model_id):
        return m
    parts = model_id.split("/")
    provider = parts[0] if len(parts) > 1 else ""
    vendor = parts[1] if len(parts) > 2 else ""
    model = parts[-1]
    return Model(provider=provider, vendor=vendor, model=model, display_name=model)
