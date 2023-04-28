# Califire Wildfires
Download wildfires data from Calfire

## Installation
```
pipenv install calfire-wildfires
```
## Command-line usage

```
Usage: calfirewildfires [OPTIONS] COMMAND [ARGS]...

    A command-line interface for downloading wildfires data from CalFire.
    Returns GeoJSON.

Options:
    --help  Show this message and exit.

Commands:
    active-fires    The latest active fires
    all-fires       Fires year-to-date, both active and contained
```

From the shell:
```
calfirewildfires all-fires
calfirewildfires active-fires
```

## Python usage
Import the library.
```
import calfire_wildfires

data = calfire_wildfires.get_all_fires()
data = calfire_wildfires.get_active_fires()
```

## Contributing
Install dependencies for development.
```
pipenv install --dev
```

Run tests.
```
pipenv run python test.py
```

## Developing the CLI
The command-line interface is implemented using Click and setuptools. To install it locally for development inside your virtual environment, run the following installation command, as prescribed by the Click documentation.
```
pipenv run pip install --editable .
```

### Links

* Docs: [palewi.re/docs/calfire-wildfires/](https://palewi.re/docs/calfire-wildfires/)
* Issues: [github.com/datadesk/calfire-wildfires/issues](https://github.com/datadesk/calfire-wildfires/issues)
* Packaging: [pypi.python.org/pypi/calfire-wildfires](https://pypi.python.org/pypi/calfire-wildfires)
* Testing: [github.com/datadesk/calfire-wildfires/actions](https://github.com/datadesk/calfire-wildfires/actions)
