"""Tests that call CAL FIRE's real website.

They are skipped unless you ask for them with ``make test-live`` (or
``uv run pytest -m live``), because they are slow and fail whenever CAL FIRE
is down.
"""

import pytest

import calfire_wildfires

pytestmark = pytest.mark.live


def test_live_all_fires():
    """The full list downloads and has the shape of a GeoJSON collection."""
    data = calfire_wildfires.get_all_fires()
    assert data["type"] == "FeatureCollection"


def test_live_active_fires():
    """The active list downloads. It can be empty when nothing is burning."""
    data = calfire_wildfires.get_active_fires()
    assert data["type"] == "FeatureCollection"


def test_live_incidents():
    """Every incident CAL FIRE lists right now can be read as a typed record."""
    for incident in calfire_wildfires.get_all_incidents():
        assert incident.started_at.tzinfo is not None
