Download wildfires data from CalFire

Hourly scrapes powered by a GitHub Action are stored in the `data` directory.

## Installation

```sh
pipenv install calfire-wildfires
```

## Command-line usage

```sh
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

```sh
calfirewildfires all-fires
calfirewildfires active-fires
```

## Python usage

Import the library. 

```python
>>> import calfire_wildfires
>>> data = calfire_wildfires.get_all_fires()
>>> data = calfire_wildfires.get_active_fires()
```

## Contributing

Install dependencies for development.

```sh
pipenv install --dev
```

Run tests.

```sh
make test
```

Ship new version to PyPI.

```sh
make ship
```

## Developing the CLI

The command-line interface is implemented using Click and setuptools. To
install it locally for development inside your virtual environment, run
the following installation command, as [prescribed by the Click
documentation](https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration).

```sh
pip install --editable .
```
