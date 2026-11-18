"""Download CAL FIRE's incident list, with a timeout and retries."""

from __future__ import annotations

import random
import sys
import time
from typing import Any

import requests

from .errors import CalFireDataError, CalFireError

BASE_URL = "https://incidents.fire.ca.gov/umbraco/api/IncidentApi/GeoJsonList"
"""The address of CAL FIRE's list of incidents."""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",  # noqa
}
"""The browser-like headers this package has always sent to CAL FIRE."""

DEFAULT_TIMEOUT = 60.0
"""How many seconds to wait for CAL FIRE before giving up on one attempt."""

DEFAULT_TRIES = 4
"""How many times to try before raising an error."""

RETRY_STATUS_CODES = frozenset({408, 429})
"""Statuses worth another try. Every 5xx status is also worth another try."""


def download_json(
    url: str,
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    tries: int = DEFAULT_TRIES,
) -> dict[str, Any]:
    """Download one of CAL FIRE's GeoJSON lists.

    A download is tried again when CAL FIRE cannot be reached, takes too long,
    or answers with a server error or "too many requests". The wait before
    each new try doubles, starting at 2 seconds. Any other bad status, such as
    "not found", fails right away.

    Args:
        url: The address to download, such as ``BASE_URL``.
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for CAL FIRE on each try. Defaults to 60.
        tries: How many tries to make in all. Defaults to 4.

    Returns:
        The GeoJSON as a dictionary, with a ``features`` list.

    Raises:
        CalFireError: If every try fails, or CAL FIRE answers with a status
            that is not worth trying again.
        CalFireDataError: If the answer arrives but is not a GeoJSON list.

    Examples:
        >>> data = download_json(BASE_URL + "?inactive=false")
        >>> data = download_json(BASE_URL, timeout=120, tries=2)
    """
    problem = None
    for attempt in range(max(tries, 1)):
        if attempt:
            time.sleep(2**attempt + random.random())
        if verbose:
            print(f"Requesting {url}", file=sys.stderr)
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as error:
            problem = CalFireError(
                f"Could not reach CAL FIRE at {url}: {error}", url=url
            )
            continue
        except requests.RequestException as error:
            raise CalFireError(f"Request to {url} failed: {error}", url=url) from error

        status = response.status_code
        if status >= 500 or status in RETRY_STATUS_CODES:
            problem = CalFireError(
                f"CAL FIRE sent back status {status} for {url}",
                url=url,
                status_code=status,
            )
            continue
        if status >= 400:
            raise CalFireError(
                f"CAL FIRE sent back status {status} for {url}",
                url=url,
                status_code=status,
            )
        return _read_json(response, url)

    assert problem is not None
    raise problem


def _read_json(response: requests.Response, url: str) -> dict[str, Any]:
    """Read the GeoJSON out of a good reply.

    Args:
        response: The reply from CAL FIRE.
        url: The address it came from, used in error messages.

    Returns:
        The GeoJSON as a dictionary.

    Raises:
        CalFireDataError: If the body is not JSON, or is not a list of features.
    """
    try:
        data = response.json()
    except ValueError as error:
        raise CalFireDataError(f"The answer from {url} is not JSON", url=url) from error
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        raise CalFireDataError(
            f"The answer from {url} does not look like a list of incidents: "
            "it has no 'features' list",
            url=url,
        )
    return data
