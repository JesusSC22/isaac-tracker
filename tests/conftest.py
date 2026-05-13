"""Shared pytest fixtures for the tracker test suite."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_save_path():
    p = FIXTURES / "sample_save_repentance_plus.dat"
    if not p.exists():
        pytest.skip("No real save fixture")
    return p


@pytest.fixture
def known_completions():
    p = FIXTURES / "sample_save_known_completions.json"
    if not p.exists():
        pytest.skip("No ground-truth notes")
    return json.loads(p.read_text())
