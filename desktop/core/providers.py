import json
import os
import urllib.error
import urllib.request

PROVIDERS = {
    "gemini": {"label": "Gemini", "env": "NEON_GEMINI_API_KEY", "kind": "gemini", "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", "model": "gemini-2.5-flash"},
    "xkiro": {"label": "xKiro", "env": "NEON_XKIRO_API_KEY", "kind": "openai", "endpoint": "https://api.xkiro.com/v1/chat/completions", "model": "auto"},
    "anthropic": {"label": "Anthropic", "env": "NEON_ANTHROPIC_API_KEY", "kind": "anthropic", "endpoint": "https://api.anthropic.com/v1/messages", "model": "claude-sonnet-5"},
    "openai": {"label": "OpenAI", "env": "NEON_OPENAI_API_KEY", "kind": "openai", "endpoint": "https://api.openai.com/v1/chat/completions", "model": "gpt-5.6-luna"},
    "groq": {"label": "Groq", "env": "NEON_GROQ_API_KEY", "kind": "openai", "endpoint": "https://api.groq.com/openai/v1/chat/completions", "model": "openai/gpt-oss-120b"},
    "openrouter": {"label": "OpenRouter", "env": "NEON_OPENROUTER_API_KEY", "kind": "openai", "endpoint": "https://openrouter.ai/api/v1/chat/completions", "model": "openrouter/auto"},
}

ROUTES = {
    "fast": ["groq", "gemini", "openrouter", "openai", "xkiro", "anthropic"],
    "reasoning": ["anthropic", "openai", "gemini", "xkiro", "openrouter", "groq"],
    "coding": ["xkiro", "anthropic", "openai", "openrouter", "groq", "gemini"],
}

class NeonProviders:
    def __init__(self, local_path=None):
        self.local_path = local_path or os.path.join(os.path.dirname(__file__), "..", "config", "providers.local.json")
        self.local = self._load_local()

    def _load_local(self):
        try:
            with open(self.local_path, "r", encoding="utf-8") as f:
                value = json.load(f)
                return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def key(self, provider_id):
        spec = PROVIDERS[provider_id]
        return str(self.local.get(provider_id) or os.getenv(spec["env"], "")).strip()

    def status(self):
        return " • ".join(
            f"{spec['label']}={'ready' if self.key(pid) else 'missing'}"
            for pid, spec in PROVIDERS.items()
        )

    def chat(self, prompt, route="fast"):
        failures = []
        for pid in ROUTES.get(route, ROUTES["fast"]):
            key = self.key(pid)
            if not key:
                continue
            spec = PROVIDERS[pid]
            try:
                if spec["kind"] == "gemini":
                    return self._gemini(spec, key, prompt)
                if spec["kind"] == "anthropic":
                    return self._anthropic(spec, key, prompt)
                return self._openai(spec, key, prompt)
            except Exception as exc:
                failures.append(f"{spec['label']}: {exc}")
        if failures:
            raise RuntimeError(" | ".join(failures[-6:]))
        raise RuntimeError("No provider keys configured")

    def _request(self, url, body, headers):
        payload = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "ignore")[:300]
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc

    def _openai(self, spec, key, prompt):
        data = self._request(
            spec["endpoint"],
            {"model": spec["model"], "messages": [{"role": "user", "content": prompt}], "max_tokens": 1200},
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "X-Title": "NEON OS"},
        )
        return data["choices"][0]["message"]["content"].strip()

    def _anthropic(self, spec, key, prompt):
        data = self._request(
            spec["endpoint"],
            {"model": spec["model"], "messages": [{"role": "user", "content": prompt}], "max_tokens": 1200},
            {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        )
        return "".join(x.get("text", "") for x in data.get("content", []) if x.get("type") == "text").strip()

    def _gemini(self, spec, key, prompt):
        data = self._request(
            f"{spec['endpoint']}?key={key}",
            {"contents": [{"parts": [{"text": prompt}]}]},
            {"Content-Type": "application/json"},
        )
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
