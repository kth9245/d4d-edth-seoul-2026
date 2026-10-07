"""Minimal frontmatter parser (stdlib only): `key: value`, `key: [a, b]`, `key: null`."""


def _value(raw: str):
    raw = raw.split(" #", 1)[0].strip()
    if raw in ("", "null", "~"):
        return None
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [v.strip().strip("'\"") for v in inner.split(",")] if inner else []
    return raw.strip("'\"")


def parse(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, raw = line.split(":", 1)
            meta[key.strip()] = _value(raw)
    body = text[end + 4 :].lstrip("\n")
    return meta, body
