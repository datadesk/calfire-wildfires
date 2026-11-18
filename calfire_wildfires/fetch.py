"""Download CAL FIRE's incident list, with a timeout and retries."""

from __future__ import annotations

import json
import random
import sys
import time
from typing import Any, Protocol

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


class Reply(Protocol):
    """What a request function must hand back: a status code and the body's bytes.

    A ``requests.Response`` fits this.
    """

    @property
    def status_code(self) -> int:
        """The web status, such as 200 or 404."""
        ...

    @property
    def content(self) -> bytes:
        """The body of the reply, as bytes."""
        ...


class Fetcher(Protocol):
    """A function that makes a web request for this package.

    Pass one as ``get`` to add retries, logging or custom headers. ``requests.get``
    fits this. The package's own default is ``requests.get`` plus the
    browser-like headers it has always sent.

    Examples:
        >>> import requests
        >>> fetcher: Fetcher = requests.get
    """

    def __call__(self, url: str, *, timeout: float) -> Reply:
        """Request a web address.

        Args:
            url: The address to request.
            timeout: The seconds to wait before giving up.

        Returns:
            The reply.
        """
        ...


def _default_get(url: str, *, timeout: float) -> Reply:
    """Request an address with ``requests.get`` and the package's headers.

    Args:
        url: The address to request.
        timeout: The seconds to wait before giving up.

    Returns:
        The ``requests`` response.
    """
    return requests.get(url, headers=HEADERS, timeout=timeout)


def download_json(
    url: str,
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    tries: int = DEFAULT_TRIES,
    get: Fetcher | None = None,
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
        get: A function that makes the web request, such as ``requests.get``.
            It is called as ``get(url, timeout=seconds)`` and must return
            something with ``status_code`` and ``content``. Its ``requests``
            errors are retried like the default's. Any other error it raises
            is passed on untouched. When it is left out, the package uses
            ``requests.get`` with the browser-like headers it has always sent.
            A function you pass is responsible for its own headers.

    Returns:
        The GeoJSON as a dictionary, with a ``features`` list.

    Raises:
        CalFireError: If every try fails, or CAL FIRE answers with a status
            that is not worth trying again.
        CalFireDataError: If the answer arrives but is not a GeoJSON list.

    Examples:
        >>> data = download_json(BASE_URL + "?inactive=false")
        >>> data = download_json(BASE_URL, timeout=120, tries=2)
        >>> data = download_json(BASE_URL, get=my_get)
    """
    fetch: Fetcher = get or _default_get
    problem = None
    for attempt in range(max(tries, 1)):
        if attempt:
            time.sleep(2**attempt + random.random())
        if verbose:
            print(f"Requesting {url}", file=sys.stderr)
        try:
            response = fetch(url, timeout=timeout)
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


def _read_json(response: Reply, url: str) -> dict[str, Any]:
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
        data = json.loads(response.content)
    except ValueError as error:
        raise CalFireDataError(f"The answer from {url} is not JSON", url=url) from error
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        raise CalFireDataError(
            f"The answer from {url} does not look like a list of incidents: "
            "it has no 'features' list",
            url=url,
        )
    return data
