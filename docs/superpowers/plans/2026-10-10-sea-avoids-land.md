# Sea Vehicles Route Around the Island — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The USV and enemy boats never cross Baengnyeong island: the scenario carries an island polygon, sim steers sea movers around it, and the demo coordinates are at sea.

**Architecture:** `Scenario.land: list[Polygon]` (contract) holds the island traced once from the local satellite tiles. `shared/land.py` does the plane geometry (inside, crossing, pushed-out corners, nearest sea point). A new sim action `sea_aim(pos, goal, land)` returns the point to steer at this tick (goal if the straight line is clear, else the first corner of the shortest path round the island). `move_straight`, `follow_route`, `orbit_or_keep` and `steer_enemies` steer at that point; `advance_vehicles` passes `land` only for sea vehicles; `engine.py` passes `sc.land`.

**Tech Stack:** Python 3.11, pydantic 2, pytest (+xdist), uv. Pillow only for the one-off tracing script (`uv run --with pillow`, not a project dependency).

**Spec:** `docs/superpowers/specs/2026-10-10-sea-avoids-land-design.md` (decision 0034, task Part2-19.1).

## Global Constraints

- Work only in the worktree `/home/kth9245/HACKERTON/KDTH2026/.claude/worktrees/Part2-19.1`. Run each shell command on its own (no `cd x && y`, no `$(...)`, no heredocs into files — the worktree guard refuses them; write scratch scripts with the Write tool into the session scratchpad).
- TDD (decision 0014): failing test first, see it fail, implement, see it pass.
- Action files: one public function named like the file, 80 lines or fewer. `engine.py` only calls in order.
- Another module only through `from modules.<m> import <public API>`; inside sim, actions may import sibling actions (`modules.sim.actions.*`). `shared/` must not import `modules`.
- No logging inside pure actions. Scripts log through `shared.log` (decision 0010).
- Happy path only (decision 0024): no extra edge-case code beyond what the spec names.
- Margins: corners pushed **100 m** out to sea; goals on land moved to **50 m** off the nearest coast (doubled up to 16x when that lands on land again).
- Sea movers = vehicles with `domain == sea` and enemies with `kind in (boat, fast_boat)`. Air and ground move exactly as today.
- Demo coordinates: USV home **37.981, 124.691**; boat1 appears at **37.985, 124.70** at 11 min and heads for the landing point; fast1 appears from boat1 at 23 min at **6.3 m/s** and heads for the east landing point **37.962, 124.744**; UGV landing point **37.982, 124.70**.
- After each task: `scripts/ship.sh` (rebase, module tests, smoke, push to main). Never ship with a failing test; never skip someone else's test.
- sim (SIM-05..08) and `engine.py` belong to 최동호: tell him in chat (through the lead) when they change.
- Code comments and docstrings follow the file they are in (sim actions: Korean docstring; shared/geo: English).

## Review Focus

1. A polygon traced clockwise instead of counter-clockwise must still give the convex corners pushed outward — test in Task 2 (`SQUARE_CW`).
2. A goal on land beside a narrow inlet, where a 50 m push lands on the opposite shore, must still end at sea — test in Task 2 (`U_SHAPE`).
3. A vehicle sitting exactly on a corner must head for the next corner, not stall on the one it is on — test in Task 4.
4. Air and ground vehicles must keep flying/driving straight over the island — test in Task 6.
5. "다음 사건으로" (`/run/jump`) runs thousands of ticks back to back; a detouring vehicle must not make it crawl — measured in Task 9 with a fix ready.

---

### Task 0: Sync and check what 최동호 already shipped

**Files:** none

- [ ] **Step 1: Rebase the worktree on main**

Run: `git fetch origin`
Run: `git rebase origin/main`
Expected: clean rebase (only the decision 0034 and design commits are ours).

- [ ] **Step 2: See whether boat1/fast1 are already enemies**

Run: `grep -n "EnemySpec\|enemies=" scripts/example_world.py`
Expected today: no output (they are still `spawn_target`/`split_target` events). If there is output, 최동호's Part1-19 landed: in Task 8 keep his enemy ids, plays and switches and change only the coordinates listed in Global Constraints.

- [ ] **Step 3: Link the venv if missing**

Run: `ls -la .venv`
Expected: a symlink to `/home/kth9245/HACKERTON/KDTH2026/.venv` (already made). If missing: `ln -s /home/kth9245/HACKERTON/KDTH2026/.venv .venv`.

---

### Task 1: Contract `Scenario.land`

**Files:**
- Modify: `contracts/models/frame.py:51-60` (class `Scenario`)
- Modify: `contracts/API.md:14` (concept table, 시나리오 row)
- Regenerate: `contracts/schema/*.json`, `modules/cop-ui/src/contracts.gen.ts` (by `scripts/gen_contracts.py`)
- Test: `tests/test_contracts.py`

**Interfaces:**
- Produces: `Scenario.land: list[Polygon] = []` (TS: `land?: Polygon[]`).

- [ ] **Step 1: Write the failing test** — append to `tests/test_contracts.py`:

```python
def test_scenario_land_is_island_polygons_and_defaults_to_none():
    sc = Scenario.model_validate(_load(EXAMPLES / "scenario.json"))
    island = Polygon(points=[GeoPoint(lat=37.94, lon=124.68), GeoPoint(lat=37.94, lon=124.72),
                             GeoPoint(lat=37.97, lon=124.70)])  # fmt: skip
    data = {k: v for k, v in sc.model_dump().items() if k != "land"}
    assert Scenario.model_validate(data).land == []
    assert Scenario.model_validate({**data, "land": [island.model_dump()]}).land == [island]
```

- [ ] **Step 2: Run it to see it fail**

Run: `uv run pytest tests/test_contracts.py -k land -n 0`
Expected: FAIL with `AttributeError: 'Scenario' object has no attribute 'land'`.

- [ ] **Step 3: Add the field** — in `contracts/models/frame.py`, class `Scenario`, after the `enemies` line:

```python
    enemies: list[EnemySpec] = []  # decision 0032
    land: list[Polygon] = []  # decision 0034: islands that sea vehicles and enemy boats go round
```

Make sure `Polygon` is imported at the top of `contracts/models/frame.py` (add it to the existing `from contracts.models.world import ...` line if it is not there).

- [ ] **Step 4: Run it to see it pass**

Run: `uv run pytest tests/test_contracts.py -n 0`
Expected: all PASS.

- [ ] **Step 5: Regenerate schema and TS**

Run: `uv run python scripts/gen_contracts.py`
Run: `git diff --stat`
Expected: `contracts/schema/scenario.json` and `modules/cop-ui/src/contracts.gen.ts` changed; `contracts.gen.ts` has `land?: Polygon[];` in `Scenario`.

- [ ] **Step 6: API.md concept row** — in `contracts/API.md` replace the 시나리오 row:

```
| 시나리오 | 시연 묶음: 작전 + 기체 제원 + 플레이 목록 + 사건 대본 + 적 + 섬(육지) 다각형 `land`(결정 0034) | `Scenario` |
```

- [ ] **Step 7: Run the contract and repo tests**

Run: `uv run pytest tests -q`
Expected: PASS.

- [ ] **Step 8: Commit and ship**

```bash
git add contracts/models/frame.py contracts/API.md contracts/schema modules/cop-ui/src/contracts.gen.ts tests/test_contracts.py
git commit -m "Part2-19.1: contract Scenario.land (island polygons, decision 0034), schema and TS regenerated"
scripts/ship.sh
```
(Commit message ends with the `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` line.)

---

### Task 2: Island geometry `shared/land.py`

**Files:**
- Create: `shared/land.py`
- Test: `tests/test_land.py`

**Interfaces:**
- Consumes: `contracts.models.GeoPoint`, `Polygon`.
- Produces (used by Tasks 3-8):
  - `Key = tuple[tuple[tuple[float, float], ...], ...]`, `key(land) -> Key`
  - `to_xy(lat, lon, ref) -> (x, y)` meters east/north of `ref=(lat, lon)`; `to_geo((x, y), ref) -> GeoPoint`
  - `rings(k) -> tuple[tuple[(x, y), ...], ...]` (cached)
  - `inside_xy(p, rs) -> bool`, `blocked_xy(a, b, rs) -> bool`
  - `corners_xy(k) -> tuple[(x, y), ...]` convex corners pushed 100 m out (cached)
  - `links_xy(k) -> tuple[tuple[int, ...], ...]` corners each corner sees (cached)
  - `inside(p: GeoPoint, land) -> bool`, `blocked(a: GeoPoint, b: GeoPoint, land) -> bool`, `to_sea(p: GeoPoint, land, margin_m=50.0) -> GeoPoint`
  - `land` everywhere is `Sequence[Polygon]`; empty means "no island" (inside/blocked False, to_sea returns p).

- [ ] **Step 1: Write the failing tests** — create `tests/test_land.py`:

```python
import math

import pytest

from contracts.models import GeoPoint, Polygon
from shared.geo import dist_m, offset_latlon
from shared.land import blocked, corners_xy, inside, key, to_sea, to_xy

C = GeoPoint(lat=37.95, lon=124.70)


def _at(east_m: float, north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(C.lat, C.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


def _poly(*pts) -> Polygon:
    return Polygon(points=[_at(e, n) for e, n in pts])


SQUARE = [_poly((-500, -500), (500, -500), (500, 500), (-500, 500))]  # counter-clockwise
SQUARE_CW = [_poly((-500, -500), (-500, 500), (500, 500), (500, -500))]
L_SHAPE = [_poly((0, 0), (1000, 0), (1000, 400), (400, 400), (400, 1000), (0, 1000))]
# Two 200 m arms with a 40 m slot between them (x -20..20, y 100..600).
U_SHAPE = [_poly((-220, 0), (220, 0), (220, 600), (20, 600), (20, 100), (-20, 100), (-20, 600),
                 (-220, 600))]  # fmt: skip


def test_inside_is_true_on_the_island_and_false_at_sea():
    assert inside(C, SQUARE)
    assert not inside(_at(-1000, 0), SQUARE)
    assert not inside(C, [])


def test_blocked_when_the_straight_line_crosses_the_island():
    assert blocked(_at(-1000, -200), _at(1000, -200), SQUARE)
    assert not blocked(_at(-1000, 800), _at(1000, 800), SQUARE)
    assert not blocked(_at(-1000, -200), _at(1000, -200), [])


def test_to_sea_moves_a_land_point_50_m_off_the_nearest_coast():
    assert dist_m(to_sea(_at(0, 400), SQUARE), _at(0, 550)) < 1
    sea = _at(-1000, 0)
    assert to_sea(sea, SQUARE) == sea
    assert to_sea(C, []) == C


def test_to_sea_pushes_past_a_narrow_inlet():
    # 10 m from the slot wall: pushes of 50, 100 and 200 m land on the other arm, 400 m is at sea
    assert not inside(to_sea(_at(-30, 300), U_SHAPE), U_SHAPE)


@pytest.mark.parametrize("land", [SQUARE, SQUARE_CW])
def test_corners_are_the_four_corners_pushed_100_m_out_either_way_round(land):
    k = key(land)
    centre = to_xy(C.lat, C.lon, k[0][0])
    cs = corners_xy(k)
    assert len(cs) == 4
    for c in cs:
        assert math.dist(c, centre) == pytest.approx(500 * math.sqrt(2) + 100, abs=1)


def test_reflex_corner_is_not_a_turning_point():
    assert len(corners_xy(key(L_SHAPE))) == 5  # six corners, one bends inward
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/test_land.py -n 0`
Expected: FAIL with `ModuleNotFoundError: No module named 'shared.land'`.

- [ ] **Step 3: Write `shared/land.py`**

```python
"""Island (land) geometry for routing sea vehicles and enemy boats round islands (decision 0034).

Math runs in local meters (x east, y north) from one reference point per land list (the first point
of the first polygon), equirectangular: well under a meter off at island size (~10 km).
Rings, corners and the corner graph are cached by the polygon coordinates, so they are built once.
"""

import math
from collections.abc import Sequence
from functools import lru_cache

from contracts.models import GeoPoint, Polygon

EARTH_RADIUS_M = 6_371_000.0
XY = tuple[float, float]
Key = tuple[tuple[tuple[float, float], ...], ...]


def key(land: Sequence[Polygon]) -> Key:
    return tuple(tuple((p.lat, p.lon) for p in poly.points) for poly in land)


def to_xy(lat: float, lon: float, ref: tuple[float, float]) -> XY:
    x = math.radians(lon - ref[1]) * EARTH_RADIUS_M * math.cos(math.radians(ref[0]))
    return (x, math.radians(lat - ref[0]) * EARTH_RADIUS_M)


def to_geo(xy: XY, ref: tuple[float, float]) -> GeoPoint:
    lat = ref[0] + math.degrees(xy[1] / EARTH_RADIUS_M)
    lon = ref[1] + math.degrees(xy[0] / (EARTH_RADIUS_M * math.cos(math.radians(ref[0]))))
    return GeoPoint(lat=lat, lon=lon)


@lru_cache(maxsize=16)
def rings(k: Key) -> tuple[tuple[XY, ...], ...]:
    ref = k[0][0]
    return tuple(tuple(to_xy(lat, lon, ref) for lat, lon in poly) for poly in k)


def _sides(ring):
    return zip(ring, ring[1:] + ring[:1])


def _cross(o: XY, a: XY, b: XY) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _unit(x: float, y: float) -> XY:
    n = math.hypot(x, y) or 1.0
    return (x / n, y / n)


def _in_ring(p: XY, ring) -> bool:
    hit = False
    for (x1, y1), (x2, y2) in _sides(ring):
        if (y1 > p[1]) != (y2 > p[1]) and p[0] < x1 + (p[1] - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def inside_xy(p: XY, rs) -> bool:
    return any(_in_ring(p, r) for r in rs)


def blocked_xy(a: XY, b: XY, rs) -> bool:
    """The segment a-b goes over land: it crosses a coast side, or its middle is on land."""
    if inside_xy(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), rs):
        return True
    for r in rs:
        for c, d in _sides(r):
            if _cross(c, d, a) * _cross(c, d, b) < 0 and _cross(a, b, c) * _cross(a, b, d) < 0:
                return True
    return False


@lru_cache(maxsize=16)
def corners_xy(k: Key) -> tuple[XY, ...]:
    """Convex coast corners pushed 100 m out to sea along the outer bisector (a shortest path round
    an island bends only there). A pushed corner that lands on land is dropped."""
    rs, out = rings(k), []
    for r in rs:
        ccw = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in _sides(r)) > 0
        s = 1.0 if ccw else -1.0
        for prev, v, nxt in zip(r[-1:] + r[:-1], r, r[1:] + r[:1]):
            turn = _cross(prev, v, nxt)
            if turn == 0 or (turn > 0) != ccw:  # straight or reflex corner
                continue
            e1, e2 = _unit(v[0] - prev[0], v[1] - prev[1]), _unit(nxt[0] - v[0], nxt[1] - v[1])
            b = _unit(s * (e1[1] + e2[1]), -s * (e1[0] + e2[0]))  # sum of the two outward normals
            c = (v[0] + b[0] * 100.0, v[1] + b[1] * 100.0)
            if not inside_xy(c, rs):
                out.append(c)
    return tuple(out)


@lru_cache(maxsize=16)
def links_xy(k: Key) -> tuple[tuple[int, ...], ...]:
    """For each corner, the other corners it sees across open sea."""
    cs, rs = corners_xy(k), rings(k)
    return tuple(
        tuple(j for j in range(len(cs)) if j != i and not blocked_xy(cs[i], cs[j], rs))
        for i in range(len(cs))
    )


def inside(p: GeoPoint, land: Sequence[Polygon]) -> bool:
    k = key(land)
    return bool(k) and inside_xy(to_xy(p.lat, p.lon, k[0][0]), rings(k))


def blocked(a: GeoPoint, b: GeoPoint, land: Sequence[Polygon]) -> bool:
    k = key(land)
    if not k:
        return False
    ref = k[0][0]
    return blocked_xy(to_xy(a.lat, a.lon, ref), to_xy(b.lat, b.lon, ref), rings(k))


def _nearest_on(p: XY, c: XY, d: XY) -> XY:
    dx, dy = d[0] - c[0], d[1] - c[1]
    t = ((p[0] - c[0]) * dx + (p[1] - c[1]) * dy) / ((dx * dx + dy * dy) or 1.0)
    t = max(0.0, min(1.0, t))
    return (c[0] + t * dx, c[1] + t * dy)


def to_sea(p: GeoPoint, land: Sequence[Polygon], margin_m: float = 50.0) -> GeoPoint:
    """p itself when at sea; on land, the nearest coast point pushed margin_m out to sea (doubled up
    to 16x when a narrow inlet puts the pushed point on the opposite shore)."""
    k = key(land)
    if not k:
        return p
    ref, rs = k[0][0], rings(k)
    q = to_xy(p.lat, p.lon, ref)
    if not inside_xy(q, rs):
        return p
    sides = [(c, d) for r in rs for c, d in _sides(r)]
    shore = min((_nearest_on(q, c, d) for c, d in sides), key=lambda s: math.dist(q, s))
    u = _unit(shore[0] - q[0], shore[1] - q[1])
    for m in (margin_m * 2**i for i in range(5)):
        out = (shore[0] + u[0] * m, shore[1] + u[1] * m)
        if not inside_xy(out, rs):
            return to_geo(out, ref).model_copy(update={"alt_m": p.alt_m})
    return p
```

- [ ] **Step 4: Run them to see them pass**

Run: `uv run pytest tests/test_land.py -n 0`
Expected: 7 PASS (the parametrized corner test counts twice).

- [ ] **Step 5: Lint**

Run: `uv run ruff check shared/land.py tests/test_land.py`
Run: `uv run ruff format --check shared/land.py tests/test_land.py`
Expected: no errors (fix formatting with `uv run ruff format shared/land.py tests/test_land.py` if needed).

- [ ] **Step 6: Commit and ship**

```bash
git add shared/land.py tests/test_land.py
git commit -m "Part2-19.1: shared/land island geometry (inside, crossing, corners pushed 100 m out, nearest sea point)"
scripts/ship.sh
```

---

### Task 3: Trace the island and put it in the scenario

**Files:**
- Create: `scripts/make_land.py`
- Create: `demo/scenarios/baengnyeong_land.json` (written by the script)
- Modify: `scripts/example_world.py` (load `LAND`, pass `land=LAND` to `Scenario`)
- Regenerate: `demo/scenarios/baengnyeong_night.json`, `contracts/examples/scenario.json` (by `scripts/gen_examples.py`)
- Test: `tests/test_demo_scenario.py`

**Interfaces:**
- Consumes: `shared.land.inside` (Task 2), `Scenario.land` (Task 1).
- Produces: `example_world.LAND: list[Polygon]` (one polygon, the main island); the demo scenario JSON has `land`.

- [ ] **Step 1: Write the failing test** — in `tests/test_demo_scenario.py` add to the imports `from contracts.models import Frame, GeoPoint, Play, Scenario` (add `GeoPoint`) and `from shared.land import inside`, then append:

```python
def test_scenario_has_the_island_traced_from_the_tiles():
    sc = Scenario.model_validate(_load(SCENARIO))
    assert len(sc.land) == 1 and 30 <= len(sc.land[0].points) <= 90
    assert inside(GeoPoint(lat=37.95, lon=124.70), sc.land)  # the drone pads are on the island
    assert not inside(GeoPoint(lat=38.0, lon=124.70), sc.land)  # NLL side is open sea
```

- [ ] **Step 2: Run it to see it fail**

Run: `uv run pytest tests/test_demo_scenario.py -k island -n 0`
Expected: FAIL (`assert 0 == 1`, the scenario has no land).

- [ ] **Step 3: Write `scripts/make_land.py`**

```python
"""Trace the main island outline from the local satellite tiles (decision 0034).

One-off data step, run again only when the tiles change. Pillow is not a project dependency:
    uv run --with pillow python scripts/make_land.py [--tol 30] [--preview out.png]
Writes demo/scenarios/baengnyeong_land.json, a Polygon list: [{"points": [{"lat", "lon"}, ...]}].
Sea is where blue > 1.5 x red (dark teal water vs green/brown land), median-filtered; the largest
land blob is the island; its outer boundary is simplified with Douglas-Peucker in meters.
"""

import argparse
import json
import math
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from shared.log import get_logger, setup_logging  # noqa: E402

TILES = ROOT / "modules" / "cop-ui" / "public" / "tiles" / "baengnyeong" / "13"
OUT = ROOT / "demo" / "scenarios" / "baengnyeong_land.json"
WORLD_PX = 256 * 2**13
log = get_logger("make_land")


def mosaic() -> tuple[Image.Image, int, int]:
    cols = sorted(int(d.name) for d in TILES.iterdir() if d.is_dir())
    rows = sorted({int(f.stem) for c in cols for f in (TILES / str(c)).glob("*.jpg")})
    img = Image.new("RGB", ((cols[-1] - cols[0] + 1) * 256, (rows[-1] - rows[0] + 1) * 256))
    for c in cols:
        for f in (TILES / str(c)).glob("*.jpg"):
            img.paste(
                Image.open(f).convert("RGB"), ((c - cols[0]) * 256, (int(f.stem) - rows[0]) * 256)
            )
    return img, cols[0] * 256, rows[0] * 256


def land_mask(img: Image.Image) -> Image.Image:
    px, m = img.load(), Image.new("L", img.size)
    mp = m.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, _, b = px[x, y]
            mp[x, y] = 0 if b > r * 1.5 else 255
    return m.filter(ImageFilter.MedianFilter(9))


def largest_blob(m: Image.Image) -> set[tuple[int, int]]:
    (w, h), mp = m.size, m.load()
    seen: set[tuple[int, int]] = set()
    best: set[tuple[int, int]] = set()
    for y0 in range(h):
        for x0 in range(w):
            if mp[x0, y0] < 128 or (x0, y0) in seen:
                continue
            blob, q = {(x0, y0)}, deque([(x0, y0)])
            while q:
                x, y = q.popleft()
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= n[0] < w and 0 <= n[1] < h and mp[n] >= 128 and n not in blob:
                        blob.add(n)
                        q.append(n)
            seen |= blob
            if len(blob) > len(best):
                best = blob
    return best


def outer_ring(blob: set[tuple[int, int]]) -> list[tuple[int, int]]:
    """Pixel-corner loop round the blob's outside with land on the right (screen y down). Where two
    diagonal pixels touch at a corner, turn right so the loop keeps to the pixel it follows."""
    out: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for x, y in blob:
        for (a, b), nb in (
            (((x, y), (x + 1, y)), (x, y - 1)),
            (((x + 1, y), (x + 1, y + 1)), (x + 1, y)),
            (((x + 1, y + 1), (x, y + 1)), (x, y + 1)),
            (((x, y + 1), (x, y)), (x - 1, y)),
        ):
            if nb not in blob:
                out.setdefault(a, []).append(b)
    start = min(blob, key=lambda p: (p[1], p[0]))
    ring, prev, cur = [start], start, (start[0] + 1, start[1])
    while cur != start:
        ring.append(cur)
        opts = out[cur]
        if len(opts) > 1:
            din = (cur[0] - prev[0], cur[1] - prev[1])
            opts = [o for o in opts if din[0] * (o[1] - cur[1]) - din[1] * (o[0] - cur[0]) > 0]
        prev, cur = cur, opts[0]
    return ring


def corner_ll(cx: int, cy: int, x0: int, y0: int) -> tuple[float, float]:
    gx, gy = cx + x0, cy + y0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * gy / WORLD_PX))))
    return lat, gx / WORLD_PX * 360.0 - 180.0


def ll_px(lat: float, lon: float, x0: int, y0: int) -> tuple[float, float]:
    gx = (lon + 180.0) / 360.0 * WORLD_PX
    gy = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * WORLD_PX
    return gx - x0, gy - y0


def _seg_dist(p, a, b) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1.0)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def simplify(xy: list[tuple[float, float]], tol: float) -> list[int]:
    """Douglas-Peucker on an open chain; the kept indices, first and last always."""
    keep, stack = {0, len(xy) - 1}, [(0, len(xy) - 1)]
    while stack:
        i, j = stack.pop()
        far, best = None, tol
        for k in range(i + 1, j):
            d = _seg_dist(xy[k], xy[i], xy[j])
            if d > best:
                far, best = k, d
        if far is not None:
            keep.add(far)
            stack += [(i, far), (far, j)]
    return sorted(keep)


def simplify_ring(xy: list[tuple[float, float]], tol: float) -> list[int]:
    far = max(range(len(xy)), key=lambda i: math.dist(xy[0], xy[i]))
    closed = xy + [xy[0]]
    a = simplify(closed[: far + 1], tol)
    b = [far + i for i in simplify(closed[far:], tol)]
    return a[:-1] + b[:-1]  # drop the repeated far point and the closing point


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tol", type=float, default=30.0, help="Douglas-Peucker tolerance, meters")
    ap.add_argument("--preview", help="also draw the polygon over the tiles into this PNG")
    a = ap.parse_args()
    setup_logging("make_land")
    img, x0, y0 = mosaic()
    blob = largest_blob(land_mask(img))
    ring = [corner_ll(cx, cy, x0, y0) for cx, cy in outer_ring(blob)]
    lat0, lon0 = ring[0]
    k = math.cos(math.radians(lat0))
    xy = [((lon - lon0) * 111_320 * k, (lat - lat0) * 111_320) for lat, lon in ring]
    pts = [ring[i] for i in simplify_ring(xy, a.tol)]
    poly = {"points": [{"lat": round(la, 5), "lon": round(lo, 5)} for la, lo in pts]}
    OUT.write_text(json.dumps([poly], indent=2) + "\n", encoding="utf-8")
    log.info("%s: %d points from %d outline corners, %d land pixels",
             OUT.relative_to(ROOT), len(pts), len(ring), len(blob))  # fmt: skip
    if a.preview:
        line = [ll_px(la, lo, x0, y0) for la, lo in pts]
        ImageDraw.Draw(img).line(line + line[:1], fill=(255, 0, 0), width=3)
        img.save(a.preview)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the script with a preview**

Run: `uv run --with pillow python scripts/make_land.py --preview /tmp/claude-1000/-home-kth9245-HACKERTON-KDTH2026/a0c674dc-ee60-42fc-a0e9-4d09721e7e41/scratchpad/land_preview.png`
Expected: a log line like `demo/scenarios/baengnyeong_land.json: 55 points from 4xxx outline corners, 2xxxxx land pixels`. If the point count is above 90, rerun with `--tol 45`; below 30, `--tol 20`.

- [ ] **Step 5: Look at the preview**

Open the PNG with the Read tool. Expected: a red outline hugging Baengnyeong's coast (north coves, the east lobe, the Sagot bay in the south-east), no loop into the sea or across the island. If it is wrong, stop and report — do not hand-edit the JSON.

- [ ] **Step 6: Load it in `scripts/example_world.py`** — add `import json` and `from pathlib import Path` at the top (standard-library imports before `from contracts.models import ...`), then after `BOAT1_SPAWN = gp(37.985, 124.70)`:

```python
# Island outline traced from the local satellite tiles by scripts/make_land.py (decision 0034).
LAND_FILE = Path(__file__).resolve().parent.parent / "demo" / "scenarios" / "baengnyeong_land.json"
LAND = [Polygon.model_validate(p) for p in json.loads(LAND_FILE.read_text(encoding="utf-8"))]
```

and in `SCENARIO = Scenario(...)` add `land=LAND,` after `events=EVENTS,`.

- [ ] **Step 7: Regenerate the examples and the demo scenario**

Run: `uv run python scripts/gen_examples.py`
Run: `git status --short`
Expected: modified `demo/scenarios/baengnyeong_night.json`, `contracts/examples/scenario.json`; new `demo/scenarios/baengnyeong_land.json`. Nothing else (if other example files changed, inspect with `git diff` — they should not).

- [ ] **Step 8: Run the tests**

Run: `uv run pytest tests/test_demo_scenario.py tests/test_contracts.py -n 0`
Expected: PASS.

- [ ] **Step 9: Commit and ship**

```bash
git add scripts/make_land.py scripts/example_world.py demo/scenarios/baengnyeong_land.json demo/scenarios/baengnyeong_night.json contracts/examples/scenario.json tests/test_demo_scenario.py
git commit -m "Part2-19.1: Baengnyeong island polygon traced from the local tiles (make_land.py) in the demo scenario"
scripts/ship.sh
```

---

### Task 4: SIM-13 `sea_aim`

**Files:**
- Create (by `new_action.py`): `modules/sim/actions/sea_aim.py`, `modules/sim/tests/test_sea_aim.py`, SPEC row SIM-13
- Modify: `modules/sim/__init__.py` (export `sea_aim`)
- Modify: `contracts/API.md` (3절 "그 밖의 공개 API", sim line)

**Interfaces:**
- Consumes: `shared.land.key, rings, to_xy, to_geo, inside_xy, blocked_xy, corners_xy, links_xy, to_sea` (Task 2).
- Produces: `sea_aim(pos: GeoPoint, goal: GeoPoint, land: Sequence[Polygon]) -> GeoPoint`, importable as `from modules.sim.actions.sea_aim import sea_aim` (inside sim) and `from modules.sim import sea_aim` (outside).

- [ ] **Step 1: Create the action skeleton**

Run: `uv run python scripts/new_action.py sim sea_aim "해상 기체·적 배가 이번 틱에 향할 점: 직선이 섬을 지나면 섬 모서리 최단 경로의 첫 모서리(결정 0034)" --inputs "pos, goal, land" --outputs "GeoPoint" --done "열린 직선이면 goal, 막히면 가까운 쪽 모서리, 모서리 위면 다음 모서리, 목표가 육지면 해안 50 m 바다 점, 육지 위 출발·land 없음이면 goal"`
Expected: SPEC row SIM-13 added, `modules/sim/actions/sea_aim.py` and a failing `modules/sim/tests/test_sea_aim.py` created.

- [ ] **Step 2: Replace the generated test** — `modules/sim/tests/test_sea_aim.py`:

```python
from contracts.models import GeoPoint, Polygon
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, offset_latlon

C = GeoPoint(lat=37.95, lon=124.70)


def _at(east_m: float, north_m: float) -> GeoPoint:
    lat, lon = offset_latlon(C.lat, C.lon, east_m, north_m)
    return GeoPoint(lat=lat, lon=lon)


ISLAND = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]
SW, SE = _at(-570.71, -570.71), _at(570.71, -570.71)  # corners pushed 100 m out to sea
WEST, EAST = _at(-1000, -200), _at(1000, -200)


def test_no_land_or_open_water_goes_straight_to_the_goal():
    assert sea_aim(WEST, EAST, []) == EAST
    north = _at(1000, 800)
    assert sea_aim(_at(-1000, 800), north, ISLAND) == north


def test_blocked_line_turns_at_the_corner_on_the_shorter_side():
    assert dist_m(sea_aim(WEST, EAST, ISLAND), SW) < 1


def test_on_a_corner_it_heads_for_the_next_corner():
    assert dist_m(sea_aim(SW, EAST, ISLAND), SE) < 1


def test_goal_on_land_becomes_the_sea_point_off_the_coast():
    assert dist_m(sea_aim(_at(0, 1000), _at(0, 400), ISLAND), _at(0, 550)) < 1


def test_start_on_land_goes_straight():
    assert sea_aim(C, EAST, ISLAND) == EAST
```

- [ ] **Step 3: Run it to see it fail**

Run: `uv run pytest modules/sim/tests/test_sea_aim.py -n 0`
Expected: FAIL with `NotImplementedError`.

- [ ] **Step 4: Write `modules/sim/actions/sea_aim.py`**

```python
"""SIM-13 sea_aim: 해상 기체·적 배가 이번 틱에 향할 점(결정 0034)
목표까지 직선이 섬(land)을 지나지 않으면 목표, 지나면 섬 모서리(바다 쪽 100 m)를 잇는 최단 경로의 첫 모서리.
목표가 육지 안이면 해안에서 50 m 바다 점으로 바꾼다. 지금 위치가 육지 안이면 돌아가지 않는다.
SPEC: modules/sim/SPEC.md#SIM-13
"""

import heapq
import math
from collections.abc import Sequence

from contracts.models import GeoPoint, Polygon
from shared.land import (
    blocked_xy,
    corners_xy,
    inside_xy,
    key,
    links_xy,
    rings,
    to_geo,
    to_sea,
    to_xy,
)


def _first_corner(p, g, cs, links, rs) -> int | None:
    """Dijkstra from p over the corners to g; the first corner of the shortest path, or None.
    A corner within 1 m of p is the one p stands on, so it is not a next step."""
    dist = {i: math.dist(p, c) for i, c in enumerate(cs)
            if math.dist(p, c) > 1 and not blocked_xy(p, c, rs)}  # fmt: skip
    first = {i: i for i in dist}
    heap = [(d, i) for i, d in dist.items()]
    heapq.heapify(heap)
    done: set[int] = set()
    best, best_first = math.inf, None
    while heap:
        d, i = heapq.heappop(heap)
        if d >= best:
            break
        if i in done:
            continue
        done.add(i)
        total = d + math.dist(cs[i], g)
        if total < best and not blocked_xy(cs[i], g, rs):
            best, best_first = total, first[i]
        for j in links[i]:
            nd = d + math.dist(cs[i], cs[j])
            if nd < dist.get(j, math.inf):
                dist[j], first[j] = nd, first[i]
                heapq.heappush(heap, (nd, j))
    return best_first


def sea_aim(pos: GeoPoint, goal: GeoPoint, land: Sequence[Polygon]) -> GeoPoint:
    k = key(land)
    if not k:
        return goal
    goal = to_sea(goal, land)
    ref, rs = k[0][0], rings(k)
    p, g = to_xy(pos.lat, pos.lon, ref), to_xy(goal.lat, goal.lon, ref)
    if inside_xy(p, rs) or not blocked_xy(p, g, rs):
        return goal
    i = _first_corner(p, g, corners_xy(k), links_xy(k), rs)
    return goal if i is None else to_geo(corners_xy(k)[i], ref)
```

- [ ] **Step 5: Run it to see it pass**

Run: `uv run pytest modules/sim/tests/test_sea_aim.py -n 0`
Expected: 5 PASS.

- [ ] **Step 6: Export it** — `modules/sim/__init__.py`: add `from modules.sim.actions.sea_aim import sea_aim` with the other imports and `"sea_aim",` in `__all__` (keep alphabetical order).

- [ ] **Step 7: API.md public line** — in `contracts/API.md` 3절 "그 밖의 공개 API", replace the sim line with:

```
- sim: `load_scenario_json(path) -> Scenario`. 레거시 `load_scenario`·`simulate`는 통합 1까지 그대로 둔다. `sea_aim(pos, goal, land) -> GeoPoint`(결정 0034): 해상 기체(domain sea)와 적 배(boat·fast_boat)는 직선이 `Scenario.land`를 지나면 섬 모서리(바다 쪽 100 m)를 돌아가고, 목표가 육지 안이면 해안에서 50 m 바다 점까지 간다.
```

- [ ] **Step 8: Module tests and lint**

Run: `uv run pytest modules/sim -q`
Run: `uv run ruff check modules/sim`
Expected: PASS, no lint errors.

- [ ] **Step 9: Commit and ship**

```bash
git add modules/sim/actions/sea_aim.py modules/sim/tests/test_sea_aim.py modules/sim/SPEC.md modules/sim/__init__.py contracts/API.md
git commit -m "Part2-19.1: sim sea_aim SIM-13, the point a sea mover steers at to go round the island"
scripts/ship.sh
```

---

### Task 5: Sea movers go round — `move_straight`, `follow_route`, `orbit_or_keep`

**Files:**
- Modify: `modules/sim/actions/move_straight.py`, `modules/sim/actions/follow_route.py`, `modules/sim/actions/orbit_or_keep.py`
- Modify: `modules/sim/SPEC.md` rows SIM-05, SIM-06, SIM-07
- Test: `modules/sim/tests/test_move_straight.py`, `test_follow_route.py`, `test_orbit_or_keep.py`

**Interfaces:**
- Consumes: `sea_aim` (Task 4), `shared.land.to_sea, blocked, inside`.
- Produces (used by Task 6): each gets a last parameter `land: Sequence[Polygon] = ()`:
  - `move_straight(st, spec, pc, dt_ms, land=())`
  - `follow_route(st, spec, pc, dt_ms, land=())`
  - `orbit_or_keep(st, spec, pc, targets, dt_ms, land=())`
  With `land=()` behaviour is exactly today's.

- [ ] **Step 1: Write the failing tests**

`modules/sim/tests/test_move_straight.py` — add `Polygon` to the `contracts.models` import, add `from shared.land import inside`, then append:

```python
ISLAND = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]
SEA = SPEC.model_copy(update={"domain": "sea", "home": _at(-1000, -200)})


def test_sea_move_goes_round_the_island_and_arrives():
    goal = _at(1000, -200)
    st, pc = _state(SEA.home), _passed(CommandKind.move, target=goal.model_dump())
    for _ in range(400):
        st = move_straight(st, SEA, pc, 1000, ISLAND)
        assert not inside(st.pos, ISLAND)
        if st.waypoint_idx == -1:
            break
    assert st.waypoint_idx == -1 and dist_m(st.pos, goal) < 1
```

`modules/sim/tests/test_follow_route.py` — add `Polygon` to the `contracts.models` import, add `from shared.land import inside`, then append:

```python
ISLAND = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]


def test_sea_route_goes_round_the_island_to_the_waypoint():
    east = _at(1000, -200)
    pc = PassedCommand(command=Command(id="c2", vehicle_id="d1", kind=CommandKind.follow_route,
                                       params={"route": [east.model_dump()]}),
                       checks=[], passed_ms=0)  # fmt: skip
    st = VehicleState(id="d1", t_ms=0, pos=_at(-1000, -200), heading_deg=0, battery_pct=100,
                      status=VehicleStatus.active, waypoint_idx=0)  # fmt: skip
    for _ in range(400):
        st = follow_route(st, SPEC, pc, 1000, ISLAND)
        assert not inside(st.pos, ISLAND)
        if st.waypoint_idx == 1:
            break
    assert st.waypoint_idx == 1 and dist_m(st.pos, east) < 1
```

`modules/sim/tests/test_orbit_or_keep.py` — add `Polygon` to the `contracts.models` import, add `from shared.land import inside`, then append:

```python
ISLAND = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]


def test_sea_keep_distance_goes_round_the_island_first():
    boat = BOAT.model_copy(update={"pos": _at(1000, -200)})
    pc = PassedCommand(command=Command(id="c3", vehicle_id="d1", kind=CommandKind.keep_distance,
                                       params={"target_id": "boat1", "distance_m": 200}),
                       checks=[], passed_ms=0)  # fmt: skip
    st = _state(_at(-1000, -200))
    for _ in range(400):
        st = orbit_or_keep(st, SPEC, pc, [boat], 1000, ISLAND)
        assert not inside(st.pos, ISLAND)
    assert dist_m(st.pos, boat.pos) == pytest.approx(200, abs=1)
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest modules/sim/tests/test_move_straight.py modules/sim/tests/test_follow_route.py modules/sim/tests/test_orbit_or_keep.py -n 0 -k "sea"`
Expected: 3 FAIL with `TypeError: ... takes 4 positional arguments but 5 were given` (6 for orbit_or_keep).

- [ ] **Step 3: `move_straight.py`** — full file:

```python
"""SIM-05 move_straight: move·return_home·hold 명령으로 1틱 직선 이동
land(해상 기체만 받음)가 있으면 섬을 돌아간다: sea_aim 점을 향해 가고, 육지 위 목표는 해안 바다 점(결정 0034).
SPEC: modules/sim/SPEC.md#SIM-05
"""

from collections.abc import Sequence

from contracts.models import (
    CommandKind,
    GeoPoint,
    PassedCommand,
    Polygon,
    VehicleSpec,
    VehicleState,
    VehicleStatus,
)
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, move_toward
from shared.land import to_sea


def move_straight(
    st: VehicleState,
    spec: VehicleSpec,
    pc: PassedCommand,
    dt_ms: int,
    land: Sequence[Polygon] = (),
) -> VehicleState:
    cmd = pc.command
    if cmd.kind == CommandKind.hold:
        return st
    home = cmd.kind == CommandKind.return_home
    tgt = to_sea(spec.home if home else GeoPoint(**cmd.params["target"]), land)
    pos = move_toward(st.pos, sea_aim(st.pos, tgt, land), spec.speed_mps * dt_ms / 1000)
    upd: dict = {"pos": pos}
    if dist_m(pos, tgt) < 1:
        upd["waypoint_idx"] = -1  # arrived: the `arrived` exit condition reads this
        if home:
            upd["status"] = VehicleStatus.maintenance
    return st.model_copy(update=upd)
```

- [ ] **Step 4: `follow_route.py`** — full file:

```python
"""SIM-06 follow_route: 경로점을 차례로 돌고 끝나면 처음으로
land(해상 기체만 받음)가 있으면 섬을 돌아가고, 육지 위 경로점은 해안 바다 점으로 본다(결정 0034).
SPEC: modules/sim/SPEC.md#SIM-06
"""

from collections.abc import Sequence

from contracts.models import GeoPoint, PassedCommand, Polygon, VehicleSpec, VehicleState
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, move_toward
from shared.land import to_sea


def follow_route(
    st: VehicleState,
    spec: VehicleSpec,
    pc: PassedCommand,
    dt_ms: int,
    land: Sequence[Polygon] = (),
) -> VehicleState:
    route = [GeoPoint(**q) for q in pc.command.params["route"]]
    i = max(st.waypoint_idx, 0) % len(route)
    wp = to_sea(route[i], land)
    pos = move_toward(st.pos, sea_aim(st.pos, wp, land), spec.speed_mps * dt_ms / 1000)
    upd: dict = {"pos": pos}
    if dist_m(pos, wp) < 1:
        upd["waypoint_idx"] = i + 1
    return st.model_copy(update=upd)
```

- [ ] **Step 5: `orbit_or_keep.py`** — change the signature and the last return; full file:

```python
"""SIM-07 orbit_or_keep: 표적 주위 선회(orbit) 또는 거리 유지(keep_distance)
멀리 있으면 먼저 날아간다(옛 스파이크는 원 위로 순간 이동해 이어받기 공백이 안 생겼다).
land(해상 기체만 받음)가 있고 표적까지 직선이 섬을 지나면 sea_aim 점으로 먼저 돌아간다(결정 0034).
SPEC: modules/sim/SPEC.md#SIM-07
"""

import math
from collections.abc import Sequence

from contracts.models import (
    CommandKind,
    GeoPoint,
    PassedCommand,
    Polygon,
    Target,
    VehicleSpec,
    VehicleState,
)
from modules.sim.actions.sea_aim import sea_aim
from shared.geo import dist_m, move_toward, offset_latlon
from shared.land import blocked


def orbit_or_keep(
    st: VehicleState,
    spec: VehicleSpec,
    pc: PassedCommand,
    targets: list[Target],
    dt_ms: int,
    land: Sequence[Polygon] = (),
) -> VehicleState:
    cmd = pc.command
    tg = next((t for t in targets if t.id == cmd.params.get("target_id")), None)
    if tg is None:
        return st
    r, step_m = float(cmd.params.get("distance_m", 150)), spec.speed_mps * dt_ms / 1000
    d = dist_m(st.pos, tg.pos)
    if cmd.kind == CommandKind.orbit and d <= r * 1.5:
        ang = math.radians(st.heading_deg) + step_m / r
        lat, lon = offset_latlon(tg.pos.lat, tg.pos.lon, r * math.sin(ang), r * math.cos(ang))
        pos = GeoPoint(lat=lat, lon=lon, alt_m=st.pos.alt_m)
        return st.model_copy(update={"heading_deg": math.degrees(ang) % 360, "pos": pos})
    if blocked(st.pos, tg.pos, land):
        return st.model_copy(
            update={"pos": move_toward(st.pos, sea_aim(st.pos, tg.pos, land), step_m)}
        )
    return st.model_copy(update={"pos": move_toward(st.pos, tg.pos, min(step_m, max(d - r, 0)))})
```

Run `uv run ruff format modules/sim/actions/orbit_or_keep.py` afterwards (the long import line gets wrapped).

- [ ] **Step 6: Run them to see them pass**

Run: `uv run pytest modules/sim -q`
Expected: all PASS (new sea tests and every old test).

- [ ] **Step 7: SPEC rows** — in `modules/sim/SPEC.md` append to the 완료 기준 cell of each row:
  - SIM-05: ` · 해상(land 인자)은 섬을 돌아가 도착(결정 0034)`
  - SIM-06: ` · 해상(land 인자)은 섬을 돌아가 경로점 도착(결정 0034)`
  - SIM-07: ` · 해상(land 인자)은 표적까지 직선이 막히면 섬을 돌아감(결정 0034)`

- [ ] **Step 8: Lint, commit and ship**

Run: `uv run ruff check modules/sim`
```bash
git add modules/sim/actions/move_straight.py modules/sim/actions/follow_route.py modules/sim/actions/orbit_or_keep.py modules/sim/tests/test_move_straight.py modules/sim/tests/test_follow_route.py modules/sim/tests/test_orbit_or_keep.py modules/sim/SPEC.md
git commit -m "Part2-19.1: sim move_straight, follow_route, orbit_or_keep take land and go round the island (SIM-05..07)"
scripts/ship.sh
```

---

### Task 6: `advance_vehicles` passes land to sea vehicles only

**Files:**
- Modify: `modules/sim/actions/advance_vehicles.py`
- Modify: `modules/sim/SPEC.md` row SIM-08
- Test: `modules/sim/tests/test_advance_vehicles.py`

**Interfaces:**
- Consumes: Task 5 signatures.
- Produces (used by Task 8): `advance_vehicles(states, specs, passed, dt_ms, targets, land=())` (public name `advance`).

- [ ] **Step 1: Write the failing test** — in `test_advance_vehicles.py` add `Polygon` to the `contracts.models` import and `enu_delta_m` to the `shared.geo` import, then append:

```python
def test_only_sea_vehicles_go_round_the_island():
    island = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]
    start, goal = _at(-1000, -200), _at(1000, -200)
    usv = SPECS["d1"].model_copy(update={"id": "usv", "domain": "sea"})
    states = [_state(start, VehicleStatus.active),
              _state(start, VehicleStatus.active).model_copy(update={"id": "usv"})]  # fmt: skip
    to_goal = {"target": goal.model_dump()}
    passed = [
        _passed(CommandKind.move, **to_goal),
        PassedCommand(
            command=Command(id="c2", vehicle_id="usv", kind=CommandKind.move, params=to_goal),
            checks=[],
            passed_ms=0,
        ),  # fmt: skip
    ]
    air, sea = advance_vehicles(states, {**SPECS, "usv": usv}, passed, 1000, [], island)
    assert enu_delta_m(start.lat, start.lon, air.pos.lat, air.pos.lon)[1] == pytest.approx(
        0, abs=0.1
    )
    assert (
        enu_delta_m(start.lat, start.lon, sea.pos.lat, sea.pos.lon)[1] < -1
    )  # toward the SW corner
```

- [ ] **Step 2: Run it to see it fail**

Run: `uv run pytest modules/sim/tests/test_advance_vehicles.py -k island -n 0`
Expected: FAIL with `TypeError: advance_vehicles() takes 5 positional arguments but 6 were given`.

- [ ] **Step 3: Change `advance_vehicles.py`** — add to the imports `from collections.abc import Sequence`, `Domain` and `Polygon` in the `contracts.models` import; change the signature and the three calls:

```python
def advance_vehicles(
    states: list[VehicleState],
    specs: dict[str, VehicleSpec],
    passed: list[PassedCommand],
    dt_ms: int,
    targets: list[Target],
    land: Sequence[Polygon] = (),
) -> list[VehicleState]:
```

```python
        sea = land if spec.domain == Domain.sea else ()  # only boats go round islands (0034)
        if kind in (K.orbit, K.keep_distance, K.strike):  # strike: fly onto the target (0033)
            st = orbit_or_keep(st, spec, pc, targets, dt_ms, sea)
        elif kind == K.follow_route:
            st = follow_route(st, spec, pc, dt_ms, sea)
        elif kind in (K.move, K.return_home, K.hold):
            st = move_straight(st, spec, pc, dt_ms, sea)
```

Also add to the module docstring's first line block: `land는 해상 기체에만 넘긴다(결정 0034).`

- [ ] **Step 4: Run to see it pass**

Run: `uv run pytest modules/sim -q`
Expected: all PASS.

- [ ] **Step 5: SPEC row** — SIM-08 입력 cell becomes `states, specs, passed: list[PassedCommand], dt_ms, targets, land` and append to 완료 기준 ` · land는 해상 기체에만(공중·지상은 직선, 결정 0034)`.

- [ ] **Step 6: Commit and ship**

```bash
git add modules/sim/actions/advance_vehicles.py modules/sim/tests/test_advance_vehicles.py modules/sim/SPEC.md
git commit -m "Part2-19.1: sim advance passes land to sea vehicles only (SIM-08)"
scripts/ship.sh
```

---

### Task 7: Enemy boats go round — `steer_enemies`

**Files:**
- Modify: `modules/sim/actions/steer_enemies.py`
- Modify: `modules/sim/SPEC.md` row SIM-12
- Test: `modules/sim/tests/test_steer_enemies.py`

**Interfaces:**
- Consumes: `sea_aim` (Task 4), `shared.land.to_sea`.
- Produces (used by Task 8): `steer_enemies(enemies, plays, targets, t_ms, dt_ms, land=())`; boats (`boat`, `fast_boat`) steer round `land`, other kinds go straight.

- [ ] **Step 1: Write the failing test** — in `test_steer_enemies.py` add `Polygon` to the `contracts.models` import, `dist_m` to the `shared.geo` import, `from shared.land import inside`, then append:

```python
def test_boats_steer_round_the_island_and_arrive():
    island = [Polygon(points=[_at(-500, -500), _at(500, -500), _at(500, 500), _at(-500, 500)])]
    goal = _at(1000, -200)
    play = Play(id="enemy_run", name="r", domains=["sea"], entry="run", approved=True, steps=[
        Step(id="run", name="run", do=Action(kind="move_to", params={"target": goal.model_dump()}))])  # fmt: skip
    enemies = [EnemySpec(id="fast1", kind="fast_boat", speed_mps=10, appear_offset_ms=0,
                         pos=_at(-1000, -200), play_id="enemy_run")]  # fmt: skip
    tg, t = _fast1(_at(-1000, -200)).model_copy(update={"play_id": "enemy_run"}), T
    for _ in range(400):
        (tg,) = steer_enemies(enemies, {"enemy_run": play}, [tg], t, 1000, island)
        if tg.waypoint_idx == -1:
            break
        lat, lon = offset_latlon(tg.pos.lat, tg.pos.lon, tg.vel_east_mps, tg.vel_north_mps)  # 1 s
        tg, t = tg.model_copy(update={"pos": GeoPoint(lat=lat, lon=lon)}), t + 1000
        assert not inside(tg.pos, island)
    assert tg.waypoint_idx == -1 and dist_m(tg.pos, goal) < 1
```

- [ ] **Step 2: Run it to see it fail**

Run: `uv run pytest modules/sim/tests/test_steer_enemies.py -k island -n 0`
Expected: FAIL with `TypeError: steer_enemies() takes 5 positional arguments but 6 were given`.

- [ ] **Step 3: Change `steer_enemies.py`** — imports: add `import math`, `from collections.abc import Sequence`, `Polygon` and `TargetKind` to the `contracts.models` import, `from modules.sim.actions.sea_aim import sea_aim`, `from shared.land import to_sea`. Add after `STOP`:

```python
BOATS = (TargetKind.boat, TargetKind.fast_boat)  # these go round islands (decision 0034)
```

Replace `_steer` and the signature/call in `steer_enemies`:

```python
def _steer(tg: Target, step: Step, speed: float, dt_ms: int, land: Sequence[Polygon]) -> Target:
    dest = _dest(step, tg.waypoint_idx) if tg.waypoint_idx >= 0 else None
    if dest is None:
        return tg.model_copy(update=STOP)
    dest = to_sea(dest, land)
    if dist_m(tg.pos, dest) <= speed * dt_ms / 1000:
        idx = -1 if step.do.kind.value == "move_to" else tg.waypoint_idx + 1
        return tg.model_copy(update={**STOP, "pos": dest, "waypoint_idx": idx})
    aim = sea_aim(tg.pos, dest, land)
    east, north = enu_delta_m(tg.pos.lat, tg.pos.lon, aim.lat, aim.lon)
    n = math.hypot(east, north) or 1.0
    return tg.model_copy(update={"vel_east_mps": speed * east / n, "vel_north_mps": speed * north / n})


def steer_enemies(
    enemies: list[EnemySpec],
    plays: dict[str, Play],
    targets: list[Target],
    t_ms: int,
    dt_ms: int,
    land: Sequence[Polygon] = (),
) -> list[Target]:
```

and in the loop: `out.append(_steer(tg, step, speed.get(tg.id, 0.0), dt_ms, land if tg.kind in BOATS else ()))`.

Add one line to the module docstring: `배(boat·fast_boat)는 land를 받아 섬을 돌아가고 육지 위 목적지는 해안 바다 점으로 본다(결정 0034).`

Check the file is 80 lines or fewer: `wc -l modules/sim/actions/steer_enemies.py`.

- [ ] **Step 4: Run to see it pass**

Run: `uv run pytest modules/sim -q`
Expected: all PASS.

- [ ] **Step 5: SPEC row** — SIM-12 입력 cell becomes `enemies, plays, targets, t_ms, dt_ms, land` and append to 완료 기준 ` · 배는 land를 돌아가 도착(결정 0034)`.

- [ ] **Step 6: Commit and ship**

```bash
git add modules/sim/actions/steer_enemies.py modules/sim/tests/test_steer_enemies.py modules/sim/SPEC.md
git commit -m "Part2-19.1: sim steer_enemies steers boats round the island (SIM-12)"
scripts/ship.sh
```

---

### Task 8: Demo at sea + engine passes land

**Files:**
- Modify: `scripts/example_world.py` (USV home, LANDING, EAST_LANDING, enemies boat1/fast1, events)
- Regenerate: `demo/scenarios/baengnyeong_night.json`, `demo/plays/*.json`, `contracts/examples/*.json` (by `scripts/gen_examples.py`)
- Modify: `modules/gateway/engine.py:37-39,71`
- Modify: `contracts/API.md` tick table rows 1.5 and 8
- Test: `tests/test_demo_scenario.py`, `tests/test_contracts.py`

**Interfaces:**
- Consumes: `advance(..., land)` (Task 6), `steer_enemies(..., land)` (Task 7), `shared.land.inside`.
- Produces: the demo scenario with the USV at sea, boat1/fast1 as enemies; `tick` routes sea movers round the island.

- [ ] **Step 1: Check 최동호's state again**

Run: `git fetch origin`
Run: `git rebase origin/main`
Run: `grep -n "EnemySpec\|track_fast_sea" scripts/example_world.py`
If enemies already exist: skip Step 4's enemy/plays/events edits and only set the coordinates in Global Constraints on his definitions (keep his ids; if his fast1 destination is on the east coast keep it). Ask the lead in chat before changing his plays.

- [ ] **Step 2: Write the failing tests** — `tests/test_demo_scenario.py`: add imports `from contracts.models import Decision, Frame, GeoPoint, Play, Scenario, TargetKind, TickInputs`, `from modules.gateway.engine import init_engine, tick`, `from modules.sim import load_scenario_json`. Replace `test_split_event_makes_a_fast_boat` with `test_fast_boat_comes_out_of_boat1`, and append the rest:

```python
def test_fast_boat_comes_out_of_boat1():
    sc = Scenario.model_validate(_load(SCENARIO))
    fast = next(e for e in sc.enemies if e.id == "fast1")
    assert fast.kind == "fast_boat" and fast.from_enemy == "boat1"


def test_sea_vehicles_and_boats_start_at_sea():
    sc = Scenario.model_validate(_load(SCENARIO))
    assert [v.id for v in sc.vehicles if v.domain == "sea" and inside(v.home, sc.land)] == []
    assert [e.id for e in sc.enemies if e.pos and inside(e.pos, sc.land)] == []


def test_ground_robot_watches_a_landing_point_on_the_shore():
    sc = Scenario.model_validate(_load(SCENARIO))
    pt = GeoPoint(**next(p for p in sc.plays if p.id == "landing").steps[0].do.params["target"])
    assert inside(pt, sc.land)
    assert not inside(GeoPoint(lat=pt.lat + 400 / 111_320, lon=pt.lon), sc.land)  # sea 400 m north


def test_nothing_at_sea_crosses_the_island():
    # smoke's operator: the first card's first choice ('근접 확인' sends the USV), then run to T+45 min
    sc = load_scenario_json(str(SCENARIO))
    es, card, frame = init_engine(sc), None, None
    sea = {v.id for v in sc.vehicles if v.domain == "sea"}
    boats = (TargetKind.boat, TargetKind.fast_boat)
    while es.t_ms < sc.operation.started_ms + 45 * 60_000:
        inputs = TickInputs()
        if card is None:
            card = next((r for r in es.reports if r.kind == "target_detected" and r.choices), None)
            if card:
                inputs = TickInputs(decisions=[Decision(id="dec-1", t_ms=es.t_ms, report_id=card.id,
                                                        choice_id=card.choices[0].id)])  # fmt: skip
        es, frame = tick(es, inputs)
        wet = [v.id for v in frame.vehicles if v.id in sea and inside(v.pos, sc.land)]
        wet += [t.id for t in frame.targets if t.kind in boats and inside(t.pos, sc.land)]
        assert not wet, (
            f"{wet} on the island at T+{(frame.t_ms - sc.operation.started_ms) // 1000} s"
        )
    assert card is not None
    assert next(v for v in frame.vehicles if v.id == "usv").play_id == "approach"
    assert any(t.id == "fast1" for t in frame.targets)
```

`tests/test_contracts.py` — in `test_vehicle_state_keeps_active_command` (the test ending with `assert sc.enemies == []`) change that last line to:

```python
    assert {e.id for e in sc.enemies} == {"boat1", "fast1"}
```

- [ ] **Step 3: Run them to see them fail**

Run: `uv run pytest tests/test_demo_scenario.py tests/test_contracts.py -n 0`
Expected: FAIL — `test_fast_boat_comes_out_of_boat1` (no enemies), `test_sea_vehicles_and_boats_start_at_sea` only if the old USV home is inside the traced island, `test_ground_robot_watches_a_landing_point_on_the_shore` (37.975 is 800 m inland, 400 m north is still land), `test_nothing_at_sea_crosses_the_island` (USV crosses), and the contracts enemies assertion.

- [ ] **Step 4: Edit `scripts/example_world.py`**

Imports: add `EnemySpec` to the `contracts.models` import.

Coordinates (replace the `LANDING` and `BOAT1_SPAWN` lines):

```python
LANDING = gp(37.982, 124.70)  # just inside the north shore; boat1 heads here (decision 0034)
EAST_LANDING = gp(37.962, 124.744)  # fast1 runs round the north-east cape to this east shore
BOAT1_SPAWN = gp(37.985, 124.70)
USV_HOME = gp(37.981, 124.691)  # at sea in the north cove, ~1.1 km from boat1 (decision 0034)
```

In `SPECS`: `_spec("usv", "수상정", "sea", 8, 720, 500, USV_HOME),`.

In `PLAYS`, append two enemy plays inside the list (after `go_home`):

```python
(
    _play(
        "enemy_boat1",
        "boat1 상륙 시도",
        ["sea"],
        [
            Step(
                id="in",
                name="상륙 지점으로",
                do=Action(kind="move_to", params={"target": LANDING.model_dump()}),
                on=[Exit(cond=Condition(kind="arrived"), go_step="wait")],
            ),
            Step(id="wait", name="해안 앞 대기", do=Action(kind="hold")),
        ],
        template=False,
    ),
)
(
    _play(
        "enemy_fast1",
        "fast1 동쪽 우회 침투",
        ["sea"],
        [
            Step(
                id="run",
                name="동쪽 상륙 지점으로",
                do=Action(kind="move_to", params={"target": EAST_LANDING.model_dump()}),
                on=[Exit(cond=Condition(kind="arrived"), go_step="wait")],
            ),
            Step(id="wait", name="상륙", do=Action(kind="hold")),
        ],
        template=False,
    ),
)
```

Replace `EVENTS` and add `ENEMIES`:

```python
EVENTS = [
    ScenarioEvent(offset_ms=19 * MIN, kind="vehicle_battery_set", params={"id": "d1", "pct": 21}),
]
# boat1/fast1 follow plays (decision 0032); sim keeps them at sea (decision 0034).
ENEMIES = [
    EnemySpec(id="boat1", kind="boat", speed_mps=1.0, appear_offset_ms=11 * MIN, pos=BOAT1_SPAWN,
              play_id="enemy_boat1"),
    EnemySpec(id="fast1", kind="fast_boat", speed_mps=6.3, appear_offset_ms=23 * MIN,
              from_enemy="boat1", play_id="enemy_fast1"),
]  # fmt: skip
```

In `SCENARIO = Scenario(...)` add `enemies=ENEMIES,` after `events=EVENTS,`.

- [ ] **Step 5: Regenerate**

Run: `uv run python scripts/gen_examples.py`
Run: `git status --short`
Expected: `demo/scenarios/baengnyeong_night.json`, new `demo/plays/enemy_boat1.json` and `demo/plays/enemy_fast1.json`, and `contracts/examples/*.json` that embed the USV home or the scenario. Look at `git diff --stat` and make sure nothing outside `demo/` and `contracts/examples/` changed.

- [ ] **Step 6: Run the data tests**

Run: `uv run pytest tests/test_demo_scenario.py tests/test_contracts.py -n 0`
Expected: everything PASS except `test_nothing_at_sea_crosses_the_island` (fast1 cuts across the north-east of the island: the engine does not pass `land` yet). If `test_sea_vehicles_and_boats_start_at_sea` fails for the USV, move `USV_HOME` north in 0.001° steps (37.982, 37.983, ...) until it passes, regenerate, and record the value with `uv run python scripts/task.py decide Part2-19.1 "수상정 home <값>(섬 다각형 밖)"`.

- [ ] **Step 7: Wire `engine.py`**

```python
    targets = steer_enemies(
        sc.enemies, plays, spawn_enemies(sc, targets, t, dt), t, dt, sc.land
    )  # 1.5 (0032; boats round islands 0034)
```

```python
    states = advance(states, specs, passed, dt, targets, sc.land)  # 8 (sea round islands 0034)
```

- [ ] **Step 8: Run to see it pass**

Run: `uv run pytest tests/test_demo_scenario.py -n 0`
Expected: all PASS.

- [ ] **Step 9: Whole regression**

Run: `uv run pytest modules/gateway modules/sim modules/play tests -q`
Run: `uv run python scripts/smoke.py`
Expected: all PASS (`test_demo_timeline` keeps s1 s2 s3 s5 s6 s4 order), smoke OK. If `test_demo_timeline` changed order, stop and report the scene times it printed — that is Part2-19 tuning to agree with 최동호, not something to fix by loosening the test.

- [ ] **Step 10: QA checklists that point at the USV**

Run: `grep -rn "usv\|37.94\b\|124.71\b" scripts/qa`
If there are hits that click the USV marker by screen position, run `scripts/qa.sh` with `scripts/dev.sh` up and fix the coordinates in those checklist steps.

- [ ] **Step 11: API.md tick rows** — replace rows 1.5 and 8 in `contracts/API.md`:

```
| 1.5 | sim | 적(결정 0032): `spawn_enemies(scenario, targets, t_ms, dt_ms) -> targets`, `steer_enemies(enemies, plays, targets, t_ms, dt_ms, land) -> targets`(배는 섬을 돌아감, 결정 0034) |
```

```
| 8 | sim | `advance(states, specs, passed, dt_ms, targets, land) -> states`(해상 기체는 섬을 돌아감, 결정 0034) |
```

- [ ] **Step 12: Commit and ship**

```bash
git add scripts/example_world.py demo contracts/examples contracts/API.md modules/gateway/engine.py tests/test_demo_scenario.py tests/test_contracts.py
git commit -m "Part2-19.1: demo at sea (USV home in the north cove, boat1/fast1 as enemies, landing on the shore) and the engine passes land to sim"
scripts/ship.sh
```

---

### Task 9: Speed check, records, notifications

**Files:**
- Maybe modify: `shared/land.py` (bounding-box precheck, only if slow)
- Modify: `demo/BUILT_HERE.md`

- [ ] **Step 1: Time a blocked `sea_aim`** — write `/tmp/claude-1000/-home-kth9245-HACKERTON-KDTH2026/a0c674dc-ee60-42fc-a0e9-4d09721e7e41/scratchpad/perf_sea_aim.py` with the Write tool:

```python
import time

from contracts.models import GeoPoint
from modules.sim import load_scenario_json, sea_aim
from shared.land import blocked

sc = load_scenario_json("demo/scenarios/baengnyeong_night.json")
a, b = (
    GeoPoint(lat=37.94, lon=124.59),
    GeoPoint(lat=37.99, lon=124.76),
)  # west of the island to the north-east
print("blocked:", blocked(a, b, sc.land))
sea_aim(a, b, sc.land)  # build the caches
t0 = time.perf_counter()
for _ in range(1000):
    sea_aim(a, b, sc.land)
print(f"blocked sea_aim: {time.perf_counter() - t0:.3f} ms per call")
```

Run: `uv run python /tmp/claude-1000/-home-kth9245-HACKERTON-KDTH2026/a0c674dc-ee60-42fc-a0e9-4d09721e7e41/scratchpad/perf_sea_aim.py`
Expected: `blocked: True` and a per-call time. Run: `uv run pytest tests/test_demo_scenario.py::test_nothing_at_sea_crosses_the_island -n 0 --durations=1` and note the seconds.

- [ ] **Step 2: Only if a blocked call is over 3 ms** — add a side bounding-box precheck to `shared/land.py` (TDD: the Task 2 tests already pin `blocked`; rerun them):

```python
@lru_cache(maxsize=16)
def _boxes(rs) -> tuple[tuple[XY, XY, float, float, float, float], ...]:
    return tuple((c, d, min(c[0], d[0]), max(c[0], d[0]), min(c[1], d[1]), max(c[1], d[1]))
                 for r in rs for c, d in _sides(r))  # fmt: skip


def blocked_xy(a: XY, b: XY, rs) -> bool:
    """The segment a-b goes over land: it crosses a coast side, or its middle is on land."""
    if inside_xy(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), rs):
        return True
    x0, x1, y0, y1 = min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])
    for c, d, cx0, cx1, cy0, cy1 in _boxes(rs):
        if cx1 < x0 or cx0 > x1 or cy1 < y0 or cy0 > y1:
            continue
        if _cross(c, d, a) * _cross(c, d, b) < 0 and _cross(a, b, c) * _cross(a, b, d) < 0:
            return True
    return False
```

Run: `uv run pytest tests/test_land.py modules/sim -q` → PASS; rerun Step 1 and note the new time. Commit `Part2-19.1: shared/land side bounding boxes before the crossing test (jump speed)` and ship.

- [ ] **Step 3: BUILT_HERE** — append this row to the `## 해커톤 중 만든 것` table in `demo/BUILT_HERE.md` (put the real KST time of the ship in the first cell):

```
| 10/10 HH:MM | contracts·sim·gateway·demo | 해상 기체·적 배 섬 우회(결정 0034): 로컬 위성 타일에서 뽑은 백령도 다각형 `Scenario.land`(scripts/make_land.py, EOX Sentinel-2 cloudless 2020 파생), sim `sea_aim`(직선이 섬을 지나면 바다 쪽 100 m 밀어낸 섬 모서리의 최단 경로), 수상정·boat1·fast1 모두 섬을 돌아감. 수상정 대기 위치는 북쪽 해안 앞바다, boat1·fast1은 적 플레이로. 엔진 경로 테스트가 작전 45분 동안 매 틱 바다 위인지 확인 | kth9245 |
```

- [ ] **Step 4: Commit and ship**

```bash
git add demo/BUILT_HERE.md
git commit -m "Part2-19.1: BUILT_HERE line for island routing"
scripts/ship.sh
```

- [ ] **Step 5: Tell the others**
  - 1-9 session (SendMessage `to: "1-9"`): `Scenario.land`(list[Polygon], 백령도 본섬 1개)가 main에 있다. 해상 플레이 점이 육지인지는 `shared/land.inside`와 같은 규칙(광선 교차)으로 판정하면 된다. 수상정 home은 37.981, 124.691.
  - 최동호 (through the lead, chat text to paste): sim SIM-05·06·07·08·12에 `land` 인자(기본 빈 목록), 새 SIM-13 `sea_aim`, engine.py가 `sc.land`를 넘김. 시나리오: boat1·fast1이 enemies(enemy_boat1·enemy_fast1 플레이), 수상정 home 북쪽 해안 앞바다, 상륙 예상 지점 37.982, 124.70, fast1 목적지 37.962, 124.744. Part1-19의 track_fast_sea·strike는 이 위에 얹어 달라.

- [ ] **Step 6: Close the task**

Run: `uv run python scripts/task.py done Part2-19.1`
Expected: `Part2-19.1 ... 완료`.
