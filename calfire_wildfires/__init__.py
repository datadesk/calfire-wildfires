"""
Download wildfires data from CalFire
"""

import requests


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
