"""Offline tests of timeouts, retries, errors and the command line, with fakes."""

import json

import pytest
import requests
from click.testing import CliRunner

import calfire_wildfires
from calfire_wildfires import CalFireDataError, CalFireError, fetch
from calfire_wildfires.cli import cmd

from .conftest import FakeResponse


@pytest.fixture
def script(monkeypatch):
    """Make ``requests.get`` play back a list of replies, one for each call.

    An item that is an exception is raised, and any other item is returned.
    Returns an object with the ``urls`` that were asked for and the ``kwargs``
    of the last call.
    """

    class Script:
        replies: list = []
        urls: list[str] = []
        kwargs: dict = {}

    play = Script()
    play.urls = []

    def get(url, **kwargs):
        play.urls.append(url)
        play.kwargs = kwargs
        reply = play.replies[len(play.urls) - 1]
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(fetch.requests, "get", get)
    return play


@pytest.fixture
def good(sample):
    """A good reply."""
    return FakeResponse(sample("all.json"))


def test_timeout_is_sent(script, good):
    """Every request carries a timeout, 60 seconds by default."""
    script.replies = [good]
    calfire_wildfires.get_all_fires()
    assert script.kwargs["timeout"] == 60.0


def test_custom_timeout_is_sent(script, good):
    """A caller can choose the timeout."""
    script.replies = [good]
    calfire_wildfires.get_all_fires(timeout=5)
    assert script.kwargs["timeout"] == 5


@pytest.mark.parametrize(
    "failure",
    [
        requests.ConnectionError("no route"),
        requests.Timeout("too slow"),
        FakeResponse(status_code=503),
        FakeResponse(status_code=502),
        FakeResponse(status_code=429),
    ],
)
def test_retries_then_succeeds(script, good, failure):
    """A network problem or a busy server is tried again."""
    script.replies = [failure, good]
    data = calfire_wildfires.get_all_fires()
    assert len(data["features"]) == 6
    assert len(script.urls) == 2


def test_gives_up_after_four_tries(script):
    """Four failures in a row raise a CalFireError."""
    script.replies = [FakeResponse(status_code=500)] * 4
    with pytest.raises(CalFireError) as caught:
        calfire_wildfires.get_all_fires()
    assert caught.value.status_code == 500
    assert len(script.urls) == 4


def test_not_found_is_not_retried(script):
    """A 404 will not get better, so it fails at once."""
    script.replies = [FakeResponse(status_code=404)]
    with pytest.raises(CalFireError, match="404"):
        calfire_wildfires.get_all_fires()
    assert len(script.urls) == 1


def test_error_is_still_an_exception(script):
    """Code that caught a plain Exception keeps working."""
    script.replies = [FakeResponse(status_code=404)]
    try:
        calfire_wildfires.get_active_fires()
    except Exception as error:
        assert isinstance(error, CalFireError)
    else:
        pytest.fail("no error was raised")


def test_other_request_errors_are_wrapped(script):
    """An error that is not worth retrying, such as a bad address, is wrapped."""
    script.replies = [requests.exceptions.InvalidURL("bad")]
    with pytest.raises(CalFireError, match="failed"):
        calfire_wildfires.get_all_fires()


def test_not_json_raises_data_error(script):
    """A page that is not JSON raises CalFireDataError."""

    reply = FakeResponse()
    reply.content = b"<html>Maintenance</html>"
    script.replies = [reply]
    with pytest.raises(CalFireDataError, match="not JSON"):
        calfire_wildfires.get_all_fires()


def test_wrong_shape_raises_data_error(script):
    """JSON without a features list raises CalFireDataError."""
    script.replies = [FakeResponse({"hello": "world"})]
    with pytest.raises(CalFireDataError, match="features"):
        calfire_wildfires.get_all_fires()


def test_data_error_is_also_a_value_error():
    """The data error can be caught as a ValueError, and as a CalFireError."""
    assert issubclass(CalFireDataError, ValueError)
    assert issubclass(CalFireDataError, CalFireError)


def test_bad_record_raises_data_error(script, sample):
    """A feature that cannot be read raises CalFireDataError."""
    data = sample("all.json")
    del data["features"][0]["properties"]["Started"]
    script.replies = [FakeResponse(data)]
    with pytest.raises(CalFireDataError, match="Started"):
        calfire_wildfires.get_all_incidents()


def test_verbose_writes_to_stderr(script, good, capsys):
    """Verbose mode prints each request to stderr, never stdout."""
    script.replies = [good]
    calfire_wildfires.get_all_fires(verbose=True)
    captured = capsys.readouterr()
    assert "Requesting" in captured.err
    assert captured.out == ""


def test_cli_prints_valid_json(fake_calfire, sample):
    """The command prints real JSON, so other programs can read it."""
    result = CliRunner().invoke(cmd, ["all-fires"])
    assert result.exit_code == 0
    assert json.loads(result.output) == sample("all.json")


def test_cli_indent(fake_calfire):
    """The indent option spreads the output over many lines."""
    result = CliRunner().invoke(cmd, ["active-fires", "--indent", "2"])
    assert result.output.count("\n") > 10


def test_cli_verbose_keeps_stdout_clean(fake_calfire):
    """Request messages go to stderr, so stdout stays valid JSON."""
    result = CliRunner().invoke(cmd, ["all-fires", "--verbose"])
    assert "Requesting" in result.stderr
    json.loads(result.stdout)


def test_cli_timeout_is_passed(fake_calfire):
    """The timeout option reaches the request."""
    CliRunner().invoke(cmd, ["all-fires", "--timeout", "7"])
    assert fake_calfire.calls[0][1]["timeout"] == 7


def test_cli_error_is_one_line(script):
    """A failure prints one clean line and exits with code 1."""
    script.replies = [FakeResponse(status_code=404)]
    result = CliRunner().invoke(cmd, ["all-fires"])
    assert result.exit_code == 1
    assert result.output.startswith("Error:")
    assert "Traceback" not in result.output
