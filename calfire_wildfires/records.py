"""Typed records for the incidents CAL FIRE publishes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .errors import CalFireDataError


@dataclass(frozen=True, slots=True)
class Incident:
    """One incident from CAL FIRE's list.

    An incident is a record that CAL FIRE keeps for an emergency it is tracking.
    Most are wildfires, but the list also holds other fires and a few other
    emergencies, such as hazardous material spills. The numbers, such as acres
    burned and percent contained, are reported by the agency and change as the
    incident goes on, so a record is only a picture of one moment.

    Attributes:
        unique_id: CAL FIRE's identifier for the incident, a long code.
        name: The incident's name, such as "Lamb Fire".
        incident_type: What kind of incident it is, as CAL FIRE labels it.
            Usually "Wildfire", but also "Fire" or "Hazmat".
        is_active: True if CAL FIRE still lists the incident as active.
        is_final: True if CAL FIRE has finished updating the incident.
        is_calfire_incident: True if CAL FIRE itself is involved in the
            response, rather than only listing another agency's incident.
        started_at: When the incident started, in UTC.
        updated_at: When CAL FIRE last changed the record, in UTC.
        extinguished_at: When the fire was put out, in UTC. None if CAL FIRE
            has not given a date.
        county: The county or counties, as CAL FIRE wrote them, such as
            "Kern, Los Angeles".
        counties: The same counties as a list, in the order CAL FIRE wrote them.
        admin_unit: The agency or unit in charge, such as "CAL FIRE Siskiyou
            Unit". None if CAL FIRE has none, or leaves it blank.
        admin_unit_url: A web address for the unit. CAL FIRE has so far left
            this empty, so it is usually None.
        location: A plain-words description of where the incident is.
        acres_burned: The area burned, in acres, as reported by CAL FIRE. None
            if CAL FIRE has not reported one.
        percent_contained: How much of the fire's edge crews have stopped from
            spreading, from 0 to 100, as reported by CAL FIRE. None if CAL FIRE
            has not reported one.
        control_statement: A short written update from CAL FIRE. None if there
            is none.
        agency_names: The names of the other agencies involved, as one piece
            of text. Empty if CAL FIRE lists none.
        latitude: Degrees north of the equator.
        longitude: Degrees east of the prime meridian, negative in the west.
        url: The incident's page on CAL FIRE's website.
        notification_desired: CAL FIRE's flag for whether notifications are
            wanted for the incident.

    Examples:
        >>> feature = {
        ...     "type": "Feature",
        ...     "geometry": {"type": "Point", "coordinates": [-123.5, 40.5]},
        ...     "properties": {
        ...         "Name": "Lamb Fire",
        ...         "UniqueId": "8f9a3173",
        ...         "Type": "Wildfire",
        ...         "IsActive": False,
        ...         "Final": True,
        ...         "CalFireIncident": True,
        ...         "Started": "2026-01-24T22:17:06Z",
        ...         "Updated": "2026-08-06T17:54:06Z",
        ...         "ExtinguishedDate": "",
        ...         "County": "Trinity",
        ...         "AdminUnit": "U.S. Forest Service Six Rivers National Forest",
        ...         "Location": "Hastings Tie Road",
        ...         "AcresBurned": 10.0,
        ...         "PercentContained": 100.0,
        ...         "Latitude": 40.5,
        ...         "Longitude": -123.5,
        ...         "Url": "https://www.fire.ca.gov/incidents/2026/1/24/lamb-fire/",
        ...     },
        ... }
        >>> incident = Incident.from_feature(feature)
        >>> incident.started_at.isoformat()
        '2026-01-24T22:17:06+00:00'
        >>> incident.acres_burned
        10.0
        >>> incident.extinguished_at is None
        True
    """

    unique_id: str
    name: str
    incident_type: str
    is_active: bool
    is_final: bool
    is_calfire_incident: bool
    started_at: datetime
    updated_at: datetime
    extinguished_at: datetime | None
    county: str
    counties: tuple[str, ...]
    admin_unit: str | None
    admin_unit_url: str | None
    location: str
    acres_burned: float | None
    percent_contained: float | None
    control_statement: str | None
    agency_names: str
    latitude: float
    longitude: float
    url: str
    notification_desired: bool

    @classmethod
    def from_feature(cls, feature: dict[str, Any]) -> Incident:
        """Build an incident from one GeoJSON feature in CAL FIRE's list.

        Args:
            feature: One item from the ``features`` list that
                ``get_all_fires`` or ``get_active_fires`` returns.

        Returns:
            The incident, with numbers and times parsed. Times are in UTC.

        Raises:
            CalFireDataError: If a field is missing or a value cannot be read.
                This is also a ``ValueError``.

        Examples:
            >>> try:
            ...     Incident.from_feature({"properties": {}})
            ... except ValueError as error:
            ...     print(error)
            CAL FIRE's incident has no 'County' field
        """
        try:
            props = feature["properties"]
            county = _text(props["County"])
            return cls(
                unique_id=props["UniqueId"],
                name=_text(props["Name"]),
                incident_type=_text(props["Type"]),
                is_active=_flag(props["IsActive"]),
                is_final=_flag(props["Final"]),
                is_calfire_incident=_flag(props["CalFireIncident"]),
                started_at=_parse_time(props["Started"]),
                updated_at=_parse_time(props["Updated"]),
                extinguished_at=_parse_optional_time(props["ExtinguishedDate"]),
                county=county,
                counties=tuple(c.strip() for c in county.split(",") if c.strip()),
                admin_unit=_optional_text(props["AdminUnit"]),
                admin_unit_url=_optional_text(props.get("AdminUnitUrl")),
                location=_text(props["Location"]),
                acres_burned=_optional_number(props["AcresBurned"]),
                percent_contained=_optional_number(props["PercentContained"]),
                control_statement=_optional_text(props.get("ControlStatement")),
                agency_names=_text(props.get("AgencyNames")),
                latitude=float(props["Latitude"]),
                longitude=float(props["Longitude"]),
                url=_text(props["Url"]),
                notification_desired=_flag(props.get("NotificationDesired", False)),
            )
        except KeyError as error:
            raise CalFireDataError(
                f"CAL FIRE's incident has no {error} field"
            ) from error
        except (TypeError, ValueError) as error:
            raise CalFireDataError(
                f"Could not read CAL FIRE's incident: {error}"
            ) from error


def _text(value: Any) -> str:
    """Turn a field into text, with a missing value becoming empty text.

    Args:
        value: A string or None.

    Returns:
        The string, or an empty string for None.

    Examples:
        >>> _text(None)
        ''
        >>> _text("Trinity")
        'Trinity'
    """
    return "" if value is None else str(value)


def _optional_text(value: Any) -> str | None:
    """Turn a field into text, with a missing or blank value becoming None.

    Args:
        value: A string or None.

    Returns:
        The string, or None if it was missing or only spaces.

    Examples:
        >>> _optional_text("")
        >>> _optional_text("Kern")
        'Kern'
    """
    text = _text(value).strip()
    return text or None


def _optional_number(value: Any) -> float | None:
    """Turn a field into a number, with a missing or blank value becoming None.

    Args:
        value: A number, numeric text, blank text or None.

    Returns:
        The number as a float, or None.

    Examples:
        >>> _optional_number(10)
        10.0
        >>> _optional_number(None)
    """
    if value is None or value == "":
        return None
    return float(value)


def _flag(value: Any) -> bool:
    """Check that a field is a true or false value.

    Args:
        value: Should be a bool.

    Returns:
        The same bool.

    Raises:
        ValueError: If the value is not a bool.

    Examples:
        >>> _flag(True)
        True
    """
    if not isinstance(value, bool):
        raise ValueError(f"expected true or false, not {value!r}")
    return value


def _parse_time(value: str) -> datetime:
    """Read one of CAL FIRE's times, such as ``2026-01-24T22:17:06Z``.

    Args:
        value: A time ending in ``Z``, which means UTC.

    Returns:
        A timezone-aware datetime in UTC.

    Raises:
        ValueError: If the text is not a time.

    Examples:
        >>> _parse_time("2026-01-24T22:17:06Z").isoformat()
        '2026-01-24T22:17:06+00:00'
    """
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _parse_optional_time(value: str | None) -> datetime | None:
    """Read one of CAL FIRE's times, where blank means there is none.

    Args:
        value: A time such as ``2026-01-29T01:00:00Z``, blank text or None.

    Returns:
        A timezone-aware datetime in UTC, or None if the value was blank.

    Examples:
        >>> _parse_optional_time("")
        >>> _parse_optional_time("2026-01-29T01:00:00Z").isoformat()
        '2026-01-29T01:00:00+00:00'
    """
    if not value:
        return None
    return _parse_time(value)
