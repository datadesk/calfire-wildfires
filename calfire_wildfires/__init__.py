#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download wildfires data from CalFire
"""
import csv
import requests
from geojson import Feature, FeatureCollection, Point


def get_fires():
    """
    Get the latest fires, both active and contained, from CalFire.

    Returns GeoJSON.
    """
    # Read CSV
    r = requests.get("http://www.fire.ca.gov/imapdata/mapdataactive.csv")
    lines = r.content.decode('utf-8').splitlines()
    reader = csv.DictReader(lines, delimiter=',')

    # Tidy it up
    tidy_reader = []
    for row in reader:
        tidy_row = dict((k.strip(), v.strip()) for k, v in row.items())
        tidy_reader.append(tidy_row)

    # Convert it to GeoJSON
    features = [Feature(
        geometry=Point(map(float, [r['incident_longitude'], r['incident_latitude']])),
        properties=r
    ) for r in tidy_reader]

    # Return it
    return FeatureCollection(features)


def get_active_fires():
    """
    Get active fires from CalFire.

    Returns GeoJSON.
    """
    fires = get_fires()['features']
    return FeatureCollection([f for f in fires if f['properties']['is_active'] == 'Y'])


def get_inactive_fires():
    """
    Get inactive fires from CalFire.

    Returns GeoJSON.
    """
    fires = get_fires()['features']
    return FeatureCollection([f for f in fires if f['properties']['is_active'] != 'Y'])
