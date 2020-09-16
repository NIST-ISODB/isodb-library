#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable-msg=line-too-long
"""Module to execute operations related to ISODB data handling"""
import click
import git

import isodbtools


@click.group()
def cli():
    # pylint: disable=unnecessary-pass
    """Master for click"""
    pass


@cli.command("tester")
def tester_fcn():
    """Test Platform for code reorganization"""
    print("in tester function")
    print(API_HOST)
    print(canonical_keys)


@cli.command("clean_json")
@click.argument("filename", type=click.Path(exists=True), nargs=1)
def clean_json_runner(filename):
    """Run the clean json function"""
    isodbtools.clean_json(filename)


@cli.command("download_isotherm")
@click.argument("isotherm", nargs=1)
def download_isotherm_runner(isotherm):
    """Run the download_isotherm function"""
    isodbtools.download_isotherm(isotherm)


@cli.command("regenerate_library")
def regenerate_isotherm_library_runner():
    """Run the regenerate_isotherm_library function"""
    isodbtools.regenerate_isotherm_library()


@cli.command("regenerate_adsorbents")
def regenerate_adsorbents_runner():
    """Run the regenerate adsorbents function"""
    isodbtools.regenerate_adsorbents()


@cli.command("regenerate_adsorbates")
def regenerate_adsorbates_runner():
    """Run the regenerate adsorbates function"""
    isodbtools.regenerate_adsorbates()


@cli.command("regenerate_bibliography")
def regenerate_bibliography_runner():
    """Run the regenerate bibliography function"""
    isodbtools.regenerate_bibliography()


@cli.command("git_log")
def git_log():
    """parse the git log"""
    print("parsing the git log")
    repo = git.Repo(SCRIPT_PATH)
    commits = list(repo.iter_commits("master", max_count=5))
    for commit in commits:
        print(commit.message)


@cli.command("post_process")
@click.argument("filename", type=click.Path(exists=True), nargs=1)
def post_process_isotherm_runner(filename):
    """Run the post_process function"""
    isodbtools.post_process(filename)


# To Do:
# Post-Process Script:
#   Do we want to deal with partial-pressure in the isotherm_data block ?
#     (appears in composition area)
#     DWS: not inclined to error check this block as it requires expert knowledge to compose
#   Handling of new adsorbent materials
#     Digitizer should include option to specify new adsorbent metadata
#   Handling of new adsorbates
#     Digitizer should include option to specify new adsorbate metadata
# Bibliographic entry generator
#   collate data from isotherms
#   if DOI exists, compare expected data to existing DB entry
#     if missing in existing, provide instructions for adding
#     if missing in expected, DO NOT add  [old data in DB is structured this way]
#   copy code from existing notebook for processing student data


@cli.command("generate_bibliography")
@click.argument("folder", type=click.Path(exists=True), nargs=1)
def generate_bibliography_runner(folder):
    """Run the bibliography generator"""
    isodbtools.generate_bibliography(folder)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
