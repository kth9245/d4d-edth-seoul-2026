from datetime import timedelta

from shared.kst import KST, now_kst


def test_now_kst_has_plus_nine_offset():
    assert KST.utcoffset(None) == timedelta(hours=9)
    assert now_kst().isoformat(timespec="seconds").endswith("+09:00")
