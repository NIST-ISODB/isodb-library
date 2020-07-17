#!/usr/bin/env python
"""Check consistency of isotherm database"""

import os
import sys
import json
import pandas as pd
import click
import collections

SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
ROOT_DIR = os.path.join(SCRIPT_PATH, os.pardir)
DOI_MAPPING_PATH = os.path.join(ROOT_DIR, "DOI_mapping.csv")
JSON_FOLDER = os.path.join(ROOT_DIR, "Library")


@click.group()
def cli():
    pass


@cli.command("doi-uniqueness")
def validate_doi_uniqueness():
    """Check uniqueness of DOIs."""
    doi_mapping = pd.read_csv(DOI_MAPPING_PATH)
    dois = doi_mapping["DOI"].str.lower()

    duplicates = [
        item for item, count in collections.Counter(list(dois)).items() if count > 1
    ]

    if duplicates:
        print("Error: Duplicate DOIs detected: {}".format(duplicates))
        sys.exit(1)


@cli.command("doi-mapping")
def validate_doi_mapping():
    """Check consistency of DOI_mapping.csv with Library/ folder."""
    doi_mapping = pd.read_csv(DOI_MAPPING_PATH, sep=",  ")
    doi_stubs = doi_mapping["DOI_Stub"].str.lower()
    doi_folders = [f.name.lower() for f in os.scandir(JSON_FOLDER) if f.is_dir()]
    doi_folders.remove("adsorbents")
    doi_folders.remove("adsorbates")

    dois_without_folder = set(doi_stubs) - set(doi_folders)
    if dois_without_folder:
        print("Error: DOIs without folder detected: {}".format(dois_without_folder))
        sys.exit(1)

    unlisted_folders = set(doi_folders) - set(doi_stubs)
    if unlisted_folders:
        print(
            "Error: Folders {} not listed in DOI mapping: {}".format(unlisted_folders)
        )
        sys.exit(1)


@cli.command("pressures")
@click.argument("filenames", type=click.Path(exists=True), nargs=-1)
def validate_pressures(filenames):
    """Check that pressures aren't negative."""

    issue_found = False

    for filename in filenames:
        with open(filename, "r") as handle:
            data = json.load(handle)

        pressures = [point["pressure"] for point in data["isotherm_data"]]

        negative_pressures = [p for p in pressures if p < 0]
        if negative_pressures:
            print(
                "Warning: Negative pressures {} found in {}".format(
                    negative_pressures, filename
                )
            )
            issue_found = True

    if issue_found:
        sys.exit(1)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
