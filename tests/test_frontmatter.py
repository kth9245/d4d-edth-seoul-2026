from tools.frontmatter import parse


def test_parse_scalars_lists_null_and_comments():
    text = (
        "---\nid: 0002\ntitle: 추적은 Kalman\nstatus: 제안   # 제안 / 확정\n"
        "modules: [tracking, assess]\nsupersedes: null\n---\n## 결정\n본문\n"
    )
    meta, body = parse(text)
    assert meta == {
        "id": "0002",
        "title": "추적은 Kalman",
        "status": "제안",
        "modules": ["tracking", "assess"],
        "supersedes": None,
    }
    assert body.startswith("## 결정")


def test_no_frontmatter_returns_empty_meta():
    assert parse("# just text\n") == ({}, "# just text\n")


def test_empty_list():
    meta, _ = parse("---\ntags: []\n---\n")
    assert meta["tags"] == []
