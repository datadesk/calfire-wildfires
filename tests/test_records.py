"""Offline tests of the typed incident records."""

import dataclasses
import doctest
from datetime import UTC, datetime

import pytest

import calfire_wildfires
from calfire_wildfires import Incident, records


def test_records_doctests():
    """The examples in the records module's docstrings are correct."""
    assert doctest.testmod(records).failed == 0


def test_first_incident(sample):
    """Numbers, flags and times are parsed, and times are in UTC."""
    incident = Incident.from_feature(sample("all.json")["features"][0])
    assert incident.name == "Lamb Fire"
    assert incident.incident_type == "Wildfire"
    assert incident.acres_burned == 10.0
    assert incident.percent_contained == 100.0
    assert incident.is_active is False
    assert incident.is_final is True
    assert incident.started_at == datetime(2026, 1, 24, 22, 17, 6, tzinfo=UTC)
    assert incident.updated_at.tzinfo is not None
    assert incident.extinguished_at is None
    assert incident.latitude == 40.506958
    assert incident.longitude == -123.506241
    assert incident.control_statement is None
    assert incident.admin_unit_url is None


def test_missing_numbers_are_none(sample):
    """The hazmat incident has no acres and no containment."""
    features = {f["properties"]["Name"]: f for f in sample("all.json")["features"]}
    incident = Incident.from_feature(features["Garden Grove HAZMAT"])
    assert incident.incident_type == "Hazmat"
    assert incident.acres_burned is None
    assert incident.percent_contained is None


def test_counties_are_split(sample):
    """A fire in two counties keeps CAL FIRE's text and also gives a list."""
    for feature in sample("all.json")["features"]:
        if "," in feature["properties"]["County"]:
            incident = Incident.from_feature(feature)
            assert len(incident.counties) == 2
            assert incident.county == ", ".join(incident.counties)
            return
    pytest.fail("the sample has no two-county incident")


def test_extinguished_date_is_parsed(sample):
    """A put-out date becomes a UTC time."""
    found = [
        Incident.from_feature(f)
        for f in sample("all.json")["features"]
        if f["properties"]["ExtinguishedDate"]
    ]
    assert found
    assert all(i.extinguished_at and i.extinguished_at.tzinfo for i in found)


def test_record_is_frozen(sample):
    """Records cannot be changed by accident."""
    incident = Incident.from_feature(sample("all.json")["features"][0])
    with pytest.raises(dataclasses.FrozenInstanceError):
        incident.name = "Other"  # type: ignore[misc]


def test_missing_field_raises(sample):
    """A feature without a field gives a clear error."""
    feature = sample("all.json")["features"][0]
    del feature["properties"]["Started"]
    with pytest.raises(ValueError, match="Started"):
        Incident.from_feature(feature)


def test_bad_number_raises(sample):
    """A value that cannot be read gives a clear error."""
    feature = sample("all.json")["features"][0]
    feature["properties"]["AcresBurned"] = "lots"
    with pytest.raises(ValueError, match="Could not read"):
        Incident.from_feature(feature)


def test_get_all_incidents(fake_calfire, sample):
    """Every feature in the list becomes a record."""
    incidents = calfire_wildfires.get_all_incidents()
    assert len(incidents) == len(sample("all.json")["features"])
    assert all(isinstance(i, Incident) for i in incidents)


def test_get_active_incidents(fake_calfire, sample):
    """The active list becomes records, all marked active."""
    incidents = calfire_wildfires.get_active_incidents()
    assert len(incidents) == len(sample("active.json")["features"])
    assert all(i.is_active for i in incidents)


def test_old_functions_still_return_json(fake_calfire, sample):
    """The original functions are unchanged."""
    assert calfire_wildfires.get_all_fires() == sample("all.json")
