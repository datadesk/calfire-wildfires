"""Shared test setup that keeps the tests off CAL FIRE's real website.

The files in ``tests/data`` are small samples. ``all.json`` holds a few real
incidents saved from CAL FIRE's list. Because no fire was burning when the
sample was saved, ``active.json`` is made from some of those same incidents,
edited by hand to look active.
"""

import json
from pathlib import Path

import pytest

DATA = Path(__file__).parent / "data"


class FakeResponse:
    """A stand-in for a ``requests`` response."""

    def __init__(self, payload=None, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.ok = status_code < 400

    def json(self):
        """Return the saved payload, like ``requests`` does."""
        return self.payload


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    """Skip the pauses between retries so the tests run fast."""
    from calfire_wildfires import fetch

    monkeypatch.setattr(fetch.time, "sleep", lambda seconds: None)


@pytest.fixture
def sample():
    """Return a function that reads a saved JSON sample by file name."""

    def read(name: str):
        return json.loads((DATA / name).read_text())

    return read


@pytest.fixture
def fake_calfire(monkeypatch, sample):
    """Replace ``requests.get`` and record what was asked for.

    The fake answers with the saved sample that matches the address: the
    active sample when the address asks for ``inactive=false``, otherwise the
    full sample. Set ``fake_calfire.status_code`` first to test a bad reply.
    """
    from calfire_wildfires import fetch

    class Fake:
        status_code = 200
        calls: list

    fake = Fake()
    fake.calls = []

    def get(url, **kwargs):
        fake.calls.append((url, kwargs))
        name = "active.json" if "inactive=false" in url else "all.json"
        return FakeResponse(sample(name), fake.status_code)

    monkeypatch.setattr(fetch.requests, "get", get)
    return fake
