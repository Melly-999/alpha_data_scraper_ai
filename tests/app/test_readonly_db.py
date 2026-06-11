from __future__ import annotations

import pytest

from app.db.readonly import assert_select_only


def test_assert_select_only_allows_select():
    assert_select_only("SELECT 1")


def test_assert_select_only_rejects_writes():
    with pytest.raises(ValueError):
        assert_select_only("UPDATE memories SET value = '{}'")
