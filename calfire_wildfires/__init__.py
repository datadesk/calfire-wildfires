"""
Download wildfires data from CalFire
"""
import requests


def get_active_fires():
    """
    Get the latest ative fires from CalFire.

    Returns GeoJSON with point geometry
    """
    # Request data
    r = requests.get("https://www.fire.ca.gov/umbraco/api/IncidentApi/GeoJsonList?inactive=false")
    if r.status_code != 200:
        raise Exception(f"Request for data failed with {r.status_code} status code")
    # Return it
    return r.json()


def get_all_fires():
    """
    Get all active and inactive fires (YTD) from CalFire.

    Returns GeoJSON with point geometry
    """
    # Request data
    r = requests.get("https://www.fire.ca.gov/umbraco/api/IncidentApi/GeoJsonList")
    if r.status_code != 200:
        raise Exception(f"Request for data failed with {r.status_code} status code")
    # Return it
    return  r.json()
