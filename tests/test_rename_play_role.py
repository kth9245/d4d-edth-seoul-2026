import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _script():
    spec = importlib.util.spec_from_file_location(
        "rename_play_role", ROOT / "scripts/rename_play_role.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_code_names_become_role_names():  # decision 0052
    r = _script().rename_text
    assert r("from modules.play import check_play") == "from modules.role import check_role"
    assert r("class PlayCheck(BaseModel): plays: list[Play]") == (
        "class RoleCheck(BaseModel): roles: list[Role]"
    )
    assert r("play_id, play_by_vehicle, rotation_plays") == (
        "role_id, role_by_vehicle, rotation_roles"
    )
    assert r("const playName = deletePlay(STATIC_PLAYS, WATCH_PLAY)") == (
        "const roleName = deleteRole(STATIC_ROLES, WATCH_ROLE)"
    )
    assert r('fetch("/plays/" + id); <NewPlayMenu className="newplay" />') == (
        'fetch("/roles/" + id); <NewRoleMenu className="newrole" />'
    )


def test_other_words_and_the_llm_message_role_stay():
    r = _script().rename_text
    s = 'display: flex; replay(); {"role": "user", "content": prompt}'
    assert r(s) == s


def test_korean_play_becomes_role_with_matching_particles():
    r = _script().rename_text
    assert r("플레이를 저장") == "Role을 저장"
    assert r("이 플레이가 쓰는 행동") == "이 Role이 쓰는 행동"
    assert r("플레이는 기체 하나") == "Role은 기체 하나"
    assert r("플레이와 작전") == "Role과 작전"
    assert r("새 플레이 · 플레이 삭제 · 플레이로") == "새 Role · Role 삭제 · Role로"


def test_paths_are_renamed_and_history_is_left_alone():
    m = _script()
    assert (
        m.rename_path("modules/play/actions/check_play.py") == "modules/role/actions/check_role.py"
    )
    assert m.rename_path("demo/plays/go_home.json") == "demo/roles/go_home.json"
    assert m.rename_path("modules/cop-ui/src/features/editor/PlayWorkflow.tsx") == (
        "modules/cop-ui/src/features/editor/RoleWorkflow.tsx"
    )
    touched = [
        "modules/play/SPEC.md",
        "AGENTS.md",
        "scripts/qa/editor.json",
        "contracts/models/play.py",
        "knowledge/spikes/rolecall_engine_proto/port/modules/runtime/actions/switch_play.py",
    ]
    left = [
        "decisions/log/0050-x.md",
        "knowledge/INDEX.md",
        "docs/research/09-x.md",
        "tasks/log.jsonl",
        "demo/BUILT_HERE.md",
        "contracts/schema/play.json",
        "contracts/examples/play.json",
        "modules/cop-ui/src/contracts.gen.ts",
        "scripts/rename_play_role.py",
        "tests/test_rename_play_role.py",
    ]
    assert all(m.should_touch(p) for p in touched)
    assert not any(m.should_touch(p) for p in left)
