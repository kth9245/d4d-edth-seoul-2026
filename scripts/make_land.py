"""Trace the main island outline from the local satellite tiles (decision 0034).

One-off data step, run again only when the tiles change. Pillow is not a project dependency:
    uv run --with pillow python scripts/make_land.py [--tol 70] [--preview out.png]
Writes demo/scenarios/baengnyeong_land.json, a Polygon list: [{"points": [{"lat", "lon"}, ...]}], and
puts the same list into the demo scenario's `land` (read and written through the Scenario model, so
the rest of the hand-tuned file stays byte for byte; gen_examples.py would overwrite that tuning).
Sea is where blue > 1.5 x red (dark teal water vs green/brown land), median-filtered and opened; the largest
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
from contracts.models import Polygon, Scenario  # noqa: E402
from shared.log import get_logger, setup_logging  # noqa: E402

TILES = ROOT / "modules" / "cop-ui" / "public" / "tiles" / "baengnyeong" / "13"
OUT = ROOT / "demo" / "scenarios" / "baengnyeong_land.json"
SCENARIO = ROOT / "demo" / "scenarios" / "baengnyeong_night.json"
WORLD_PX = 256 * 2**13
log = get_logger("make_land")


def mosaic() -> tuple[Image.Image, int, int]:
    cols = sorted(int(d.name) for d in TILES.iterdir() if d.is_dir())
    rows = sorted({int(f.stem) for c in cols for f in (TILES / str(c)).glob("*.jpg")})
    img = Image.new("RGB", ((cols[-1] - cols[0] + 1) * 256, (rows[-1] - rows[0] + 1) * 256))
    for c in cols:
        for f in (TILES / str(c)).glob("*.jpg"):
            at = ((c - cols[0]) * 256, (int(f.stem) - rows[0]) * 256)
            img.paste(Image.open(f).convert("RGB"), at)
    return img, cols[0] * 256, rows[0] * 256


def land_mask(img: Image.Image) -> Image.Image:
    px, m = img.load(), Image.new("L", img.size)
    mp = m.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, _, b = px[x, y]
            mp[x, y] = 0 if b > r * 1.5 else 255
    # Median removes speckle; min-then-max removes strips thinner than ~9 px (~140 m), such as the
    # bright seam between two tile rows west of the island that otherwise joins it as a fake spit.
    m = m.filter(ImageFilter.MedianFilter(9))
    return m.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9))


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
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1.0)
    t = max(0.0, min(1.0, t))
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


def put_into_scenario(land: list[Polygon]) -> None:
    sc = Scenario.model_validate_json(SCENARIO.read_text(encoding="utf-8"))
    sc = sc.model_copy(update={"land": land})
    SCENARIO.write_text(sc.model_dump_json(indent=1) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    # 70 m keeps the coves and capes (94 points) under the 100 m corner push of shared/land.
    ap.add_argument("--tol", type=float, default=70.0, help="Douglas-Peucker tolerance, meters")
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
    put_into_scenario([Polygon.model_validate(poly)])
    log.info("%s and %s: %d points from %d outline corners, %d land pixels",
             OUT.relative_to(ROOT), SCENARIO.relative_to(ROOT), len(pts), len(ring),
             len(blob))  # fmt: skip
    if a.preview:
        line = [ll_px(la, lo, x0, y0) for la, lo in pts]
        ImageDraw.Draw(img).line(line + line[:1], fill=(255, 0, 0), width=3)
        img.save(a.preview)


if __name__ == "__main__":
    main()
