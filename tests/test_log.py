import logging
import time

from shared.log import FORMAT, KSTFormatter, get_logger, setup_logging


def test_setup_logging_writes_file_and_is_idempotent(tmp_path):
    root = logging.getLogger()
    for h in list(root.handlers):  # another test (gateway create_app) may have set it up already
        if getattr(h, "_kdth", False):
            root.removeHandler(h)
            h.close()
    before = list(root.handlers)
    try:
        path = setup_logging("t", log_dir=tmp_path)
        setup_logging("t", log_dir=tmp_path)
        get_logger("x").warning("hello %d", 7)
        for h in root.handlers:
            h.flush()
        text = path.read_text(encoding="utf-8")
        assert "W kdth.x: hello 7" in text
        assert sum(1 for h in root.handlers if getattr(h, "_kdth", False)) == 2
    finally:
        for h in list(root.handlers):
            if getattr(h, "_kdth", False):
                root.removeHandler(h)
                h.close()
        assert root.handlers == before


def test_formatter_writes_kst_even_when_machine_is_utc(monkeypatch):
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    try:
        rec = logging.LogRecord("kdth.x", logging.INFO, __file__, 1, "hi", None, None)
        rec.created, rec.msecs = 0.0, 0.0
        out = KSTFormatter(FORMAT).format(rec)
        assert out.startswith("1970-01-01 09:00:00,000+0900 I kdth.x: hi")
    finally:
        monkeypatch.undo()
        time.tzset()
