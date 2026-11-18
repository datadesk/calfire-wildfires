"""Download wildfires data from CalFire"""

from __future__ import annotations

from .errors import CalFireDataError, CalFireError
from .fetch import BASE_URL, DEFAULT_TIMEOUT, Fetcher, Reply, download_json
from .records import Incident

__all__ = [
    "CalFireDataError",
    "CalFireError",
    "Fetcher",
    "Incident",
    "Reply",
    "get_active_fires",
    "get_active_incidents",
    "get_all_fires",
    "get_all_incidents",
]

ACTIVE_URL = f"{BASE_URL}?inactive=false"


def get_active_fires(
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> dict:
    """Get the latest active fires from CAL FIRE.

    Args:
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for CAL FIRE on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``.
            Pass your own to add retries, logging or custom headers. It is
            called as ``get(url, timeout=seconds)``. Defaults to
            ``requests.get`` with the headers this package has always sent.

    Returns:
        GeoJSON with point geometry, as a dictionary. It has no features when
        CAL FIRE lists no active incidents.

    Raises:
        CalFireError: If CAL FIRE cannot be reached after several tries, or
            answers with an error. This is a plain ``Exception``, as before.
        CalFireDataError: If CAL FIRE's answer is not a list of incidents.

    Examples:
        >>> import calfire_wildfires
        >>> data = calfire_wildfires.get_active_fires()
        >>> data = calfire_wildfires.get_active_fires(timeout=10)
        >>> data = calfire_wildfires.get_active_fires(get=my_get)
    """
    return download_json(ACTIVE_URL, verbose=verbose, timeout=timeout, get=get)


def get_all_fires(
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> dict:
    """Get all active and inactive fires year to date from CAL FIRE.

    Args:
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for CAL FIRE on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``.
            Pass your own to add retries, logging or custom headers. It is
            called as ``get(url, timeout=seconds)``. Defaults to
            ``requests.get`` with the headers this package has always sent.

    Returns:
        GeoJSON with point geometry, as a dictionary.

    Raises:
        CalFireError: If CAL FIRE cannot be reached after several tries, or
            answers with an error. This is a plain ``Exception``, as before.
        CalFireDataError: If CAL FIRE's answer is not a list of incidents.

    Examples:
        >>> import calfire_wildfires
        >>> data = calfire_wildfires.get_all_fires()
        >>> data = calfire_wildfires.get_all_fires(timeout=10)
        >>> data = calfire_wildfires.get_all_fires(get=my_get)
    """
    return download_json(BASE_URL, verbose=verbose, timeout=timeout, get=get)


def get_active_incidents(
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> list[Incident]:
    """Get the latest active incidents from CAL FIRE as typed records.

    This is the same list as ``get_active_fires``, with each feature turned
    into an ``Incident`` that has parsed numbers and UTC times.

    Args:
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for CAL FIRE on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``.
            Pass your own to add retries, logging or custom headers. It is
            called as ``get(url, timeout=seconds)``. Defaults to
            ``requests.get`` with the headers this package has always sent.

    Returns:
        A list of ``Incident`` records. It is empty when CAL FIRE lists no
        active incidents.

    Raises:
        CalFireError: If CAL FIRE cannot be reached after several tries, or
            answers with an error.
        CalFireDataError: If the answer, or an incident in it, cannot be read.

    Examples:
        >>> import calfire_wildfires
        >>> for incident in calfire_wildfires.get_active_incidents():
        ...     print(incident.name, incident.acres_burned, incident.percent_contained)
    """
    data = get_active_fires(verbose=verbose, timeout=timeout, get=get)
    return [Incident.from_feature(f) for f in data["features"]]


def get_all_incidents(
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> list[Incident]:
    """Get all active and inactive incidents year to date as typed records.

    This is the same list as ``get_all_fires``, with each feature turned into
    an ``Incident`` that has parsed numbers and UTC times.

    Args:
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for CAL FIRE on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``.
            Pass your own to add retries, logging or custom headers. It is
            called as ``get(url, timeout=seconds)``. Defaults to
            ``requests.get`` with the headers this package has always sent.

    Returns:
        A list of ``Incident`` records.

    Raises:
        CalFireError: If CAL FIRE cannot be reached after several tries, or
            answers with an error.
        CalFireDataError: If the answer, or an incident in it, cannot be read.

    Examples:
        >>> import calfire_wildfires
        >>> incidents = calfire_wildfires.get_all_incidents()
        >>> big = [i for i in incidents if (i.acres_burned or 0) > 10_000]
    """
    data = get_all_fires(verbose=verbose, timeout=timeout, get=get)
    return [Incident.from_feature(f) for f in data["features"]]
