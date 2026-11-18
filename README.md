# calfire-wildfires

Download California wildfire incidents from [CAL FIRE](https://www.fire.ca.gov/incidents), as GeoJSON or typed Python records.

**An incident is a record that CAL FIRE keeps for an emergency it is tracking.** Most are wildfires, but the list also holds other fires and a few other emergencies, such as hazardous material spills. Figures like acres burned and percent contained are reported by the agency and change as an incident goes on.

## Install

```sh
uv add calfire-wildfires
```

## Use it from the command line

```sh
calfirewildfires active-fires > active.json
calfirewildfires all-fires --indent 2 > all.json
calfirewildfires all-fires --timeout 120 --verbose
```

`active-fires` lists incidents CAL FIRE still shows as active. `all-fires` lists every incident this year, active or not. The output is GeoJSON.

## Use it from Python

```python
import calfire_wildfires

data = calfire_wildfires.get_active_fires()  # GeoJSON, as a dictionary
incidents = calfire_wildfires.get_all_incidents()  # typed records
for incident in incidents[:3]:
    print(incident.name, incident.started_at, incident.acres_burned)
```

## Use your own request function

Some projects send every web request through their own helper, for shared retries, logging or proxy settings. Pass that helper as `get` and the package will use it instead of `requests.get`. It is called like `get(url, timeout=seconds)` and must return something with a `status_code` and the answer's `content` as bytes. The timeout and the retries still work, and failures still raise `CalFireError`.

```python
import requests

import calfire_wildfires
from calfire_wildfires import Reply


def my_get(url: str, *, timeout: float) -> Reply:
    return requests.get(url, timeout=timeout, headers={"User-Agent": "my-project"})


data = calfire_wildfires.get_all_fires(get=my_get)
```

The `Fetcher` and `Reply` types describe this. Your function sets its own headers. Without `get`, the package sends the browser-like `User-Agent` it has always sent. CAL FIRE's website pages refuse some automated requests, so keep a browser-like one if you see "Access Denied".

## Things to know

* **Numbers change.** Acres burned and percent contained are reported by CAL FIRE and are updated, and sometimes revised, as the incident goes on. Many fields can be empty.
* **Small fires are often missing.** From CAL FIRE's own notes, we understand that fires of fewer than 10 acres generally get no information on its site. We could not confirm this from the agency's pages when we wrote this, so check them.
* **Not for emergencies.** Do not use this as your only source for evacuation or fire behavior news. Use CAL FIRE and your local officials.
* **Downloads retry.** A request waits 60 seconds, then tries again on network errors and server errors, and raises `calfire_wildfires.CalFireError` if it still fails.
* **The data comes from CAL FIRE.** The package only downloads it. CAL FIRE's own terms are on [its website](https://www.fire.ca.gov/incidents). The code is MIT.
* **AI helped write this package.** AI tools assisted in writing its code, tests and documentation. A person directed and reviewed the work.

The documentation has the full field reference.

## Working on the code

The scraped data files were saved to this repository for years. Copy only the latest version:

```bash
git clone --depth 1 https://github.com/datadesk/calfire-wildfires.git
```

### Links

* Docs: [palewi.re/docs/calfire-wildfires/](https://palewi.re/docs/calfire-wildfires/)
* Issues: [github.com/datadesk/calfire-wildfires/issues](https://github.com/datadesk/calfire-wildfires/issues)
* Packaging: [pypi.python.org/pypi/calfire-wildfires](https://pypi.python.org/pypi/calfire-wildfires)
* Testing: [github.com/datadesk/calfire-wildfires/actions](https://github.com/datadesk/calfire-wildfires/actions)
