import json
import os
from pathlib import Path

import openai


def try_model(model_name):
    kwargs = {"input": ["hello", "I like hiking."]}
    if model_name != "default":
        kwargs["model"] = model_name
    response = openai.Moderation.create(**kwargs)
    model_returned = getattr(response, "model", None)
    if model_returned is None and isinstance(response, dict):
        model_returned = response.get("model")
    return model_returned or model_name


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set")
    openai.api_key = api_key

    candidates = ["text-moderation-stable", "omni-moderation-latest", "default"]
    attempts = []
    selected = None
    for candidate in candidates:
        try:
            returned = try_model(candidate)
            attempts.append({"candidate": candidate, "status": "ok", "returned_model": returned})
            selected = candidate
            break
        except Exception as exc:
            attempts.append({
                "candidate": candidate,
                "status": "failed",
                "error_type": type(exc).__name__,
                "error": str(exc)[:300],
            })

    if selected is None:
        print(json.dumps({"ok": False, "attempts": attempts}, indent=2))
        raise SystemExit(1)

    label = "EXACT-PAPER-API" if selected == "text-moderation-stable" else "RECONSTRUCTED-CURRENT-API"
    result = {"ok": True, "selected": selected, "label": label, "attempts": attempts}
    Path("results").mkdir(exist_ok=True)
    Path("results/openai_moderation_smoke.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
