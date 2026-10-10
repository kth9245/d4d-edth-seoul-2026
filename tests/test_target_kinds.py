"""Raid enemy kinds for the 24h operation (docs/superpowers/specs/2026-10-10-24h-enemies-design.md)."""

from contracts.models import TargetKind


def test_target_kind_has_raid_kinds():
    assert {"drone", "usv", "ugv"} <= {k.value for k in TargetKind}
