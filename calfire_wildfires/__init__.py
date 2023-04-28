"""
Download wildfires data from CalFire
"""
import requests


def get_active_fires():
    """Get the latest ative fires from CalFire.

    Returns GeoJSON with point geometry
    """

    print("Requesting active Fires")
    # Request data
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36', # noqa
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', # noqa
               'Accept-Language': 'en-US,en;q=0.9'
               }
    r = requests.get(
        "https://www.fire.ca.gov/umbraco/api/IncidentApi/GeoJsonList?inactive=false",
        headers=headers
    )
    if r.status_code != 200:
        raise Exception(f"Request for data failed with {r.status_code} status code")
    # Return it
    return r.json()


def get_all_fires():
    """Get all active and inactive fires year to date from CalFire.

    Returns GeoJSON with point geometry
    """
    # Request data
    r = requests.get("https://www.fire.ca.gov/umbraco/api/IncidentApi/GeoJsonList")
    if r.status_code != 200:
        raise Exception(f"Request for data failed with {r.status_code} status code")
    # Return it
    return r.json()
