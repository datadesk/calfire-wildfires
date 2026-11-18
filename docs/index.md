# calfire-wildfires

Download California wildfire incidents from [CAL FIRE](https://www.fire.ca.gov/incidents)

```{contents} Table of contents
:local:
:depth: 2
```

## Read this first

**An incident is a record that CAL FIRE keeps for an emergency it is tracking.** It is not a map of where a fire is burning right now.

* **What is in the list.** Most incidents are wildfires. The list also holds other fires, and a few other emergencies such as hazardous material spills. The `incident_type` field says which. Each incident is one point, not the shape of the burned area.
* **How fresh it is.** The package downloads what CAL FIRE's website serves at that moment. CAL FIRE says the information is updated frequently, but the `updated_at` field is the only way to know when a given incident last changed.
* **The figures are reported, and they change.** Acres burned and percent contained come from the agency. They are updated as crews learn more, and can go up, or sometimes down, when a fire is mapped again. Either can be empty.
* **Some fires are missing.** We understand from CAL FIRE's own notes that fires under about 10 acres generally get no information on its site. We could not confirm the exact wording when this was written, so read the notes on [CAL FIRE's incidents page](https://www.fire.ca.gov/incidents).
* **Not for emergencies.** Do not rely on this package for evacuation or fire behavior news. Use CAL FIRE and your local officials.

```{note}
We could not read CAL FIRE's own terms of use or disclaimer text from a script, because its website refuses automated requests for those pages. This page therefore does not quote them. Read them on CAL FIRE's website, and credit CAL FIRE when you share the data.
```

## Installation

```bash
uv add calfire-wildfires
```

## Quick start

From the shell, print every incident this year as GeoJSON.

```bash
calfirewildfires all-fires > all.json
```

From Python, ask for typed records and read their fields.

```python
import calfire_wildfires

for incident in calfire_wildfires.get_all_incidents():
    print(incident.name, incident.counties, incident.acres_burned)
```

## Command-line usage

```bash
# Incidents CAL FIRE shows as active. It prints an empty list when there are none.
calfirewildfires active-fires

# Every incident this year, active or not, spread over several lines
calfirewildfires all-fires --indent 2 > all.json

# Wait up to two minutes for each try, and print each request to stderr
calfirewildfires all-fires --timeout 120 --verbose > all.json
```

The output is JSON, on standard output. The `--verbose` messages go to standard error, so they never mix into the JSON. If CAL FIRE cannot be reached, the command prints one line starting with `Error:` and exits with code 1.

```{note}
This changed in the release that added the typed records. Earlier versions printed Python's text form (single quotes, `True`) instead of JSON. The commands now print real JSON.
```

## Python usage

### GeoJSON

`get_active_fires` and `get_all_fires` return GeoJSON as a dictionary, exactly as CAL FIRE sends it.

```python
import calfire_wildfires

data = calfire_wildfires.get_all_fires()
print(len(data["features"]))
```

### Typed records

`get_active_incidents` and `get_all_incidents` return a list of `Incident` records. Numbers are real numbers, times are in UTC, and empty values are `None`.

```python
incidents = calfire_wildfires.get_all_incidents()
big = [i for i in incidents if (i.acres_burned or 0) > 10_000]
```

### Errors and retries

Each request waits 60 seconds (change it with `timeout=`). It is tried again, up to four times, after a network error, a timeout, a server error or "too many requests". If it still fails, `CalFireError` is raised, with the web address and the status code when there is one. If CAL FIRE answers but the answer cannot be read, `CalFireDataError` is raised. It is also a `ValueError`.

```python
try:
    data = calfire_wildfires.get_active_fires(timeout=30)
except calfire_wildfires.CalFireError as error:
    print("CAL FIRE is not answering:", error)
```

### Use your own request function

Pass `get` to use your own web request function, which is called like `get(url, timeout=seconds)` and returns something with `status_code` and `content` (bytes). The `Fetcher` and `Reply` types describe it. Your function sets its own headers. Without it, the package sends a browser-like `User-Agent`, which this package has always sent. We found that CAL FIRE's website pages refuse some automated requests, although its data address answered one without it, so the header may not be required.

```python
import requests

from calfire_wildfires import Reply


def my_get(url: str, *, timeout: float) -> Reply:
    return requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})


data = calfire_wildfires.get_all_fires(get=my_get)
```

## Field reference

These are the fields CAL FIRE publishes for each incident, with the matching `Incident` field. The meanings below are our reading of the data. CAL FIRE does not publish a field guide that we could find.

| CAL FIRE field | `Incident` field | What it means |
| --- | --- | --- |
| `UniqueId` | `unique_id` | CAL FIRE's identifier for the incident. |
| `Name` | `name` | The incident's name, such as "Lamb Fire". |
| `Type` | `incident_type` | The kind of incident. We have seen `Wildfire`, `Fire` and `Hazmat`. |
| `IsActive` | `is_active` | True if CAL FIRE lists the incident as active. |
| `Final` | `is_final` | True if CAL FIRE has finished updating the incident. |
| `CalFireIncident` | `is_calfire_incident` | True if CAL FIRE itself is involved, not only listing another agency's incident. |
| `Started` | `started_at` | When the incident started, in UTC. |
| `Updated` | `updated_at` | When CAL FIRE last changed the record, in UTC. |
| `ExtinguishedDate` | `extinguished_at` | When the fire was put out, in UTC. `None` when blank. |
| `County` | `county`, `counties` | The county or counties. `county` is CAL FIRE's text, such as `Kern, Los Angeles`, and `counties` is the same as a tuple. |
| `AdminUnit` | `admin_unit` | The agency or unit in charge. `None` when blank. |
| `AdminUnitUrl` | `admin_unit_url` | A web address for the unit. It has been empty in every record we saw. |
| `Location` | `location` | A description of where it is, in words. |
| `AcresBurned` | `acres_burned` | Acres burned, as reported by CAL FIRE. `None` when not reported. |
| `PercentContained` | `percent_contained` | How much of the fire's edge crews have stopped from spreading, 0 to 100, as reported by CAL FIRE. `None` when not reported. |
| `ControlStatement` | `control_statement` | A short written update. Mostly empty. `None` when blank. |
| `AgencyNames` | `agency_names` | Other agencies involved, as one piece of text. Mostly empty. |
| `Latitude`, `Longitude` | `latitude`, `longitude` | The point CAL FIRE gives for the incident, in degrees. Longitude is negative in the west. |
| `Url` | `url` | The incident's page on CAL FIRE's website. |
| `NotificationDesired` | `notification_desired` | CAL FIRE's flag for whether notifications are wanted. Its exact use is not documented. |

CAL FIRE also sends `ExtinguishedDateOnly` and `StartedDateOnly`, plain dates that matched the UTC times in every record we checked. The record leaves them out.

## About this package

* **Not official.** This package is not run or endorsed by CAL FIRE.
* **AI helped write this package.** AI tools assisted in writing its code, tests and documentation. A person directed and reviewed the work.

## Contributing

The scraped data files were saved to the repository for years, so copy only the latest version.

```bash
git clone --depth 1 https://github.com/datadesk/calfire-wildfires.git
cd calfire-wildfires
uv sync --all-groups
```

Run the offline tests, the linter and the type checker.

```bash
make check
```

`make test` also measures test coverage, including branches, and fails if it drops below 95%. `make test-fast` runs the tests without coverage.

The tests that call CAL FIRE's real website are skipped by default. Run them with `make test-live`.

## Developing the CLI

The command-line interface is implemented using Click. `uv sync` installs the package in editable form, so the `calfirewildfires` command is ready to use with `uv run`.

```bash
uv run calfirewildfires --help
```

## Other resources

* Issues: [github.com/datadesk/calfire-wildfires/issues](https://github.com/datadesk/calfire-wildfires/issues)
* Packaging: [pypi.python.org/pypi/calfire-wildfires](https://pypi.python.org/pypi/calfire-wildfires)
* Testing: [github.com/datadesk/calfire-wildfires/actions](https://github.com/datadesk/calfire-wildfires/actions)
