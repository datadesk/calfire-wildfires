"""Offline tests of the optional ``get`` argument, with a fake function."""

import pytest
import requests

import calfire_wildfires
from calfire_wildfires import CalFireDataError, CalFireError, fetch

from .conftest import FakeResponse


class Recorder:
    """A fake request function that plays back replies and remembers each call."""

    def __init__(self, *replies) -> None:
        self.replies = list(replies)
        self.urls: list[str] = []
        self.timeouts: list[float] = []

    def __call__(self, url: str, *, timeout: float) -> FakeResponse:
        self.urls.append(url)
        self.timeouts.append(timeout)
        reply = self.replies[min(len(self.urls), len(self.replies)) - 1]
        if isinstance(reply, Exception):
            raise reply
        return reply


@pytest.fixture
def good(sample):
    """A good reply."""
    return FakeResponse(sample("all.json"))


@pytest.fixture
def no_requests(monkeypatch):
    """Fail the test if the package falls back to ``requests.get``."""

    def refuse(*args, **kwargs):
        raise AssertionError("requests.get should not be called")

    monkeypatch.setattr(fetch.requests, "get", refuse)


def test_types_are_exported():
    """The two types are part of the public package."""
    assert calfire_wildfires.Fetcher is fetch.Fetcher
    assert calfire_wildfires.Reply is fetch.Reply
    assert {"Fetcher", "Reply"} <= set(calfire_wildfires.__all__)


def test_function_is_used_instead_of_requests(no_requests, good):
    """The caller's function makes the request, and requests is never used."""
    get = Recorder(good)
    data = calfire_wildfires.get_all_fires(get=get)
    assert len(data["features"]) == 6
    assert get.urls == [fetch.BASE_URL]


def test_active_address(no_requests, sample):
    """The active list asks for the active address."""
    get = Recorder(FakeResponse(sample("active.json")))
    calfire_wildfires.get_active_fires(get=get)
    assert get.urls == [fetch.BASE_URL + "?inactive=false"]


def test_timeout_reaches_the_function(no_requests, good):
    """The timeout is passed along, 60 seconds by default."""
    get = Recorder(good, good)
    calfire_wildfires.get_all_fires(get=get)
    calfire_wildfires.get_all_fires(timeout=5, get=get)
    assert get.timeouts == [60.0, 5]


def test_incident_functions_accept_get(no_requests, good, sample):
    """The typed functions take the argument too."""
    assert len(calfire_wildfires.get_all_incidents(get=Recorder(good))) == 6
    active = FakeResponse(sample("active.json"))
    assert len(calfire_wildfires.get_active_incidents(get=Recorder(active))) == 3


def test_retries_requests_errors(no_requests, good):
    """A requests error from the caller's function is retried."""
    get = Recorder(requests.Timeout("slow"), FakeResponse(status_code=503), good)
    data = calfire_wildfires.get_all_fires(get=get)
    assert len(data["features"]) == 6
    assert len(get.urls) == 3


def test_gives_up_with_calfire_error(no_requests):
    """Four failures in a row raise CalFireError, and a 404 is not retried."""
    get = Recorder(FakeResponse(status_code=500))
    with pytest.raises(CalFireError):
        calfire_wildfires.get_all_fires(get=get)
    assert len(get.urls) == 4
    get = Recorder(FakeResponse(status_code=404))
    with pytest.raises(CalFireError):
        calfire_wildfires.get_all_fires(get=get)
    assert len(get.urls) == 1


def test_other_errors_are_passed_on(no_requests):
    """An error that is not from requests reaches the caller untouched."""
    with pytest.raises(KeyError):
        calfire_wildfires.get_all_fires(get=Recorder(KeyError("mine")))


def test_bad_body_raises_data_error(no_requests):
    """A reply that is not a list of incidents raises CalFireDataError."""
    reply = FakeResponse()
    reply.content = b"nope"
    with pytest.raises(CalFireDataError):
        calfire_wildfires.get_all_fires(get=Recorder(reply))


def test_reply_needs_only_status_and_content(no_requests, good):
    """A minimal reply object without ``ok`` or ``json`` is enough."""

    class Minimal:
        status_code = 200
        content = good.content

    assert calfire_wildfires.get_all_fires(get=Recorder(Minimal()))["features"]


def test_default_path_sends_headers(fake_calfire):
    """Without ``get``, requests is used with the browser-like headers."""
    calfire_wildfires.get_all_fires()
    assert "Mozilla" in fake_calfire.calls[0][1]["headers"]["User-Agent"]
