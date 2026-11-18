"""Offline tests of the download functions and the command line."""

import pytest
from click.testing import CliRunner

import calfire_wildfires
from calfire_wildfires.cli import cmd


def test_all_fires_returns_the_json(fake_calfire, sample):
    """The full list is passed back exactly as CAL FIRE sent it."""
    assert calfire_wildfires.get_all_fires() == sample("all.json")
    url, kwargs = fake_calfire.calls[0]
    assert url == "https://incidents.fire.ca.gov/umbraco/api/IncidentApi/GeoJsonList"
    assert "Mozilla" in kwargs["headers"]["User-Agent"]


def test_active_fires_asks_for_active_only(fake_calfire, sample):
    """The active list uses the inactive=false address."""
    assert calfire_wildfires.get_active_fires() == sample("active.json")
    assert fake_calfire.calls[0][0].endswith("GeoJsonList?inactive=false")


@pytest.mark.parametrize(
    "func", [calfire_wildfires.get_all_fires, calfire_wildfires.get_active_fires]
)
def test_bad_status_raises(fake_calfire, func):
    """A failed request raises an exception that names the status code."""
    fake_calfire.status_code = 503
    with pytest.raises(Exception, match="503"):
        func()


@pytest.mark.parametrize("command", ["all-fires", "active-fires"])
def test_cli_commands_run(fake_calfire, command):
    """Both commands exist, run and print something."""
    result = CliRunner().invoke(cmd, [command])
    assert result.exit_code == 0
    assert "FeatureCollection" in result.output
