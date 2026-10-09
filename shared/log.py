"""Project logging (decision 0010): same lines to stderr and logs/<name>.log, always on.

Usage at a process boundary (gateway app, tick loop, scripts):
    from shared.log import setup_logging, get_logger
    setup_logging("gateway")          # once per process; safe to call twice
    log = get_logger("gateway.engine")
    log.debug("t=%d cmds=%d blocks=%d", t_ms, len(cmds), len(blocks))
Pure action functions do not log (80-line limit, reproducible tests).
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from shared.kst import KST

FORMAT = "%(asctime)s %(levelname).1s %(name)s: %(message)s"
ROOT = Path(__file__).resolve().parent.parent


class KSTFormatter(logging.Formatter):
    """asctime in KST whatever the machine timezone (decision 0012)."""

    def formatTime(self, record, datefmt=None):
        t = datetime.fromtimestamp(record.created, KST)
        return t.strftime("%Y-%m-%d %H:%M:%S") + f",{int(record.msecs):03d}+0900"


def setup_logging(name: str, level: str | None = None, log_dir: Path | None = None) -> Path:
    """Attach stderr + file handlers to the root logger once. Returns the log file path."""
    lvl = (level or os.environ.get("KDTH_LOG_LEVEL") or "DEBUG").upper()
    log_dir = log_dir or Path(os.environ.get("KDTH_LOG_DIR") or ROOT / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{name}.log"
    root = logging.getLogger()
    root.setLevel(lvl)
    if not any(getattr(h, "_kdth", False) for h in root.handlers):
        fmt = KSTFormatter(FORMAT)
        for h in (logging.StreamHandler(), logging.FileHandler(path, encoding="utf-8")):
            h.setFormatter(fmt)
            h._kdth = True  # type: ignore[attr-defined]
            root.addHandler(h)
    logging.getLogger("kdth").debug("logging to %s (level %s)", path, lvl)
    return path


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"kdth.{name}")
