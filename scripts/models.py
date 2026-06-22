from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    provider: str
    vendor: str
    model: str
    display_name: str

    @property
    def id(self) -> str:
        if self.vendor:
            return f"{self.provider}/{self.vendor}/{self.model}"
        return f"{self.provider}/{self.model}"


REGISTRY: list[Model] = [
    Model("openrouter", "anthropic", "claude-haiku-4.5", "Claude Haiku 4.5"),
    Model("openrouter", "anthropic", "claude-opus-4.8", "Claude Opus 4.8"),
    Model("openrouter", "anthropic", "claude-sonnet-4.6", "Claude Sonnet 4.6"),
    Model("openrouter", "deepseek", "deepseek-r1-0528", "DeepSeek R1 0528"),
    Model("openrouter", "deepseek", "deepseek-v4-flash", "DeepSeek V4 Flash"),
    Model("openrouter", "deepseek", "deepseek-v4-pro", "DeepSeek V4 Pro"),
    Model("openrouter", "google", "gemini-3.1-pro-preview", "Gemini 3.1 Pro Preview"),
    Model("openrouter", "google", "gemini-3.5-flash", "Gemini 3.5 Flash"),
    Model("openrouter", "google", "gemma-4-31b-it", "Gemma 4 31B"),
    Model("openrouter", "meta-llama", "llama-4-maverick", "Llama 4 Maverick"),
    Model("openrouter", "meta-llama", "llama-4-scout", "Llama 4 Scout"),
    Model("openrouter", "minimax", "minimax-m3", "MiniMax M3"),
    Model("openrouter", "mistralai", "mistral-medium-3-5", "Mistral Medium 3.5"),
    Model("openrouter", "moonshotai", "kimi-k2.6", "Kimi K2.6"),
    Model("openrouter", "nvidia", "nemotron-3-ultra-550b-a55b", "Nemotron 3 Ultra"),
    Model("openrouter", "openai", "gpt-5-mini", "GPT-5 Mini"),
    Model("openrouter", "openai", "gpt-5.5", "GPT-5.5"),
    Model("openrouter", "openai", "gpt-oss-120b", "gpt-oss-120b"),
    Model("openrouter", "qwen", "qwen3-235b-a22b-2507", "Qwen3 235B A22B Instruct 2507"),
    Model("openrouter", "qwen", "qwen3.5-397b-a17b", "Qwen3.5 397B A17B"),
    Model("openrouter", "qwen", "qwen3.7-max", "Qwen3.7 Max"),
    Model("openrouter", "x-ai", "grok-4.3", "Grok 4.3"),
    Model("openrouter", "xiaomi", "mimo-v2.5-pro", "MiMo-V2.5-Pro"),
    Model("openrouter", "z-ai", "glm-5.2", "GLM 5.2"),
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
