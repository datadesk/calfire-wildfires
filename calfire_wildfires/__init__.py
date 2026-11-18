"""
Download wildfires data from CalFire
"""

import requests

from .records import Incident

__all__ = [
    "Incident",
    "get_active_fires",
    "get_active_incidents",
    "get_all_fires",
    "get_all_incidents",
]


def get_active_fires():
    """Get the latest ative fires from CalFire.

    Returns GeoJSON with point geometry
    """
    # Request data
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",  # noqa
    }
    url = "https://incidents.fire.ca.gov/umbraco/api/IncidentApi/GeoJsonList?inactive=false"
    r = requests.get(url, headers=headers)

    # Make sure get a good response
    try:
        assert r.ok
    except AssertionError as err:
        raise Exception(
            f"Request for data failed with {r.status_code} status code"
        ) from err

    # Return it
    return r.json()


def get_all_fires():
    """Get all active and inactive fires year to date from CalFire.

    Returns GeoJSON with point geometry
    """
    # Request data
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",  # noqa
    }
    url = "https://incidents.fire.ca.gov/umbraco/api/IncidentApi/GeoJsonList"
    r = requests.get(url, headers=headers)

    # Make sure the response works
    try:
        assert r.ok
    except AssertionError as err:
        raise Exception(
            f"Request for data failed with {r.status_code} status code"
        ) from err

    # Return it
    return r.json()


def get_active_incidents() -> list[Incident]:
    """Get the latest active incidents from CAL FIRE as typed records.

    This is the same list as ``get_active_fires``, with each feature turned
    into an ``Incident`` that has parsed numbers and UTC times.

    Returns:
        A list of ``Incident`` records. It is empty when CAL FIRE lists no
        active incidents.

    Raises:
        Exception: If CAL FIRE answers with an error status.
        ValueError: If an incident in the list cannot be read.

    Examples:
        >>> import calfire_wildfires
        >>> for incident in calfire_wildfires.get_active_incidents():
        ...     print(incident.name, incident.acres_burned, incident.percent_contained)
    """
    return [Incident.from_feature(f) for f in get_active_fires()["features"]]


def get_all_incidents() -> list[Incident]:
    """Get all active and inactive incidents year to date as typed records.

    This is the same list as ``get_all_fires``, with each feature turned into
    an ``Incident`` that has parsed numbers and UTC times.

    Returns:
        A list of ``Incident`` records.

    Raises:
        Exception: If CAL FIRE answers with an error status.
        ValueError: If an incident in the list cannot be read.

    Examples:
        >>> import calfire_wildfires
        >>> incidents = calfire_wildfires.get_all_incidents()
        >>> big = [i for i in incidents if (i.acres_burned or 0) > 10_000]
    """
    return [Incident.from_feature(f) for f in get_all_fires()["features"]]
