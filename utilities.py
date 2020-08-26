#!/usr/bin/env python

import os
import pprint
import json
import requests
import unicodedata
import time
import copy
import click
import glob
import git

from config import *


@click.group()
def cli():
    pass


@cli.command("tester")
def tester_fcn():
    """Test Platform for code reorganization"""
    print("in tester function")
    print(API_HOST)
    print(canonical_keys)


@cli.command("clean_json")
@click.argument("filename", type=click.Path(exists=True), nargs=1)
def clean_json(filename):
    """Read in JSON and output according to ISODB specs"""
    print("operate on filename: ", filename)
    with open(filename, mode="r") as infile:
        isotherm_data = json.load(infile)
    os.rename(filename, filename + ".bak")
    json_writer(filename, isotherm_data)
    os.remove(filename + ".bak")


@cli.command("download_isotherm")
@click.argument("isotherm", nargs=1)
def download_isotherm(isotherm):
    """Download a specific isotherm from the ISODB and format to ISODB specs"""
    if isotherm[-5:] != ".json":
        isotherm += ".json"
    print("Downloading Isotherm: ", isotherm)
    url = API_HOST + "/isodb/api/isotherm/" + isotherm
    isotherm_data = json.loads(requests.get(url, headers=HEADERS).content)
    json_writer(isotherm, isotherm_data)


@cli.command("regenerate_library")
def regenerate_isotherm_library():
    """Generate the entire ISODB library from the API"""
    # Create the JSON Library folder if necessary
    if not os.path.exists(JSON_FOLDER):
        os.mkdir(JSON_FOLDER)

    # Generate a DOI list from the ISODB API
    url = API_HOST + "/isodb/api/biblio.json"
    bibliography = json.loads(requests.get(url, headers=HEADERS).content)
    print(len(bibliography), "Bibliography Entries")

    # Count isotherms for DOIs in the database
    url = API_HOST + "/isodb/api/isotherms.json"
    isotherms_list = json.loads(requests.get(url, headers=HEADERS).content)
    isotherm_count = {}
    for isotherm in isotherms_list:
        doi = isotherm["DOI"].lower()
        if doi not in isotherm_count:
            isotherm_count[doi] = 1
        else:
            isotherm_count[doi] += 1
    print(len(isotherms_list), "Isotherm Files")

    # Create a CSV file with the DOI -> folder mapping
    DOI_mapping = open(DOI_MAPPING_PATH, mode="w")
    DOI_mapping.write('DOI,  "DOI_Stub"\n')

    # Download and Organize the Isotherms
    article_count = 0
    for article in bibliography:
        # print(article["isotherms"])

        # Shorten the DOI according to rules specified in global variables
        doi = article["DOI"]
        doi_stub = article["DOI"]
        for rule in doi_stub_rules:
            doi_stub = doi_stub.replace(rule["old"], rule["new"])

        num_isotherms = len(article["isotherms"])
        # print(doi, doi_stub, num_isotherms)

        # Download the isotherms
        if num_isotherms > 0:
            article_count += 1
            DOI_FOLDER = os.path.join(JSON_FOLDER, doi_stub)
            # print(DOI_FOLDER)
            if not os.path.exists(DOI_FOLDER):
                os.mkdir(DOI_FOLDER)
            DOI_mapping.write(doi + ", " + doi_stub + "\n")

            for isotherm in article["isotherms"]:
                url = API_HOST + "/isodb/api/isotherm/" + isotherm["filename"] + ".json"
                isotherm_JSON = json.loads(requests.get(url, headers=HEADERS).content)
                # print(json.dumps(isotherm_JSON, sort_keys=True))
                filename = os.path.join(DOI_FOLDER, isotherm["filename"] + ".json")
                # print(filename)
                json_writer(filename, isotherm_JSON)
                # break
            print(doi, "Finished")

            # break

        # if article_count > 50: break
        if article_count % 10 == 0:
            time.sleep(5)  # slow down API calls to not overwhelm the server
        # break

    print(article_count, "Objects with Isotherms")
    DOI_mapping.close()


@cli.command("regenerate_adsorbents")
def regenerate_adsorbents():
    """Generate the entire ISODB library from the API"""
    # Create the JSON Library folder if necessary
    if not os.path.exists(JSON_FOLDER):
        os.mkdir(JSON_FOLDER)

    # Create subfolder for Adsorbents if necessary
    Adsorbent_folder = JSON_FOLDER + "/Adsorbents"
    if not os.path.exists(Adsorbent_folder):
        os.mkdir(Adsorbent_folder)

    # Generate a list of adsorbents from the MATDB API
    url = API_HOST + "/matdb/api/materials.json"
    adsorbents = json.loads(requests.get(url, headers=HEADERS).content)
    print(len(adsorbents), "Adsorbent Material Entries")

    # Extract each adsorbent in full form
    for (material_count, adsorbent) in enumerate(adsorbents):
        filename = adsorbent["hashkey"] + ".json"
        url = API_HOST + "/matdb/api/material/" + filename
        print(url)
        adsorbent_data = json.loads(requests.get(url, headers=HEADERS).content)
        # pprint.pprint(adsorbent_data)
        # Write to JSON
        json_writer(Adsorbent_folder + "/" + filename, adsorbent_data)
        if material_count % 100 == 0:
            time.sleep(5)  # slow down API calls to not overwhelm the server


@cli.command("regenerate_adsorbates")
def regenerate_adsorbates():
    """Generate the entire ISODB library from the API"""
    # Create the JSON Library folder if necessary
    if not os.path.exists(JSON_FOLDER):
        os.mkdir(JSON_FOLDER)

    # Create subfolder for Adsorbates if necessary
    Adsorbate_folder = JSON_FOLDER + "/Adsorbates"
    if not os.path.exists(Adsorbate_folder):
        os.mkdir(Adsorbate_folder)

    # Generate a list of adsorbents from the MATDB API
    url = API_HOST + "/isodb/api/gases.json"
    adsorbates = json.loads(requests.get(url, headers=HEADERS).content)
    print(len(adsorbates), "Adsorbate Species Entries")

    # Extract each adsorbate in full form
    for (adsorbate_count, adsorbate) in enumerate(adsorbates):
        filename = adsorbate["InChIKey"] + ".json"
        url = API_HOST + "/isodb/api/gas/" + filename
        print(url)
        try:
            adsorbate_data = json.loads(requests.get(url, headers=HEADERS).content)
            # pprint.pprint(adsorbate_data)
            # Write to JSON
            json_writer(Adsorbate_folder + "/" + filename, adsorbate_data)
        except:
            print("ERROR: ", adsorbate)
        # if adsorbate_count > 5: break
        if adsorbate_count % 100 == 0:
            time.sleep(5)  # slow down API calls to not overwhelm the server


@cli.command("regenerate_bibliography")
def regenerate_bibliography():
    """Generate the entire ISODB library from the API"""
    # Create the JSON Library folder if necessary
    if not os.path.exists(JSON_FOLDER):
        os.mkdir(JSON_FOLDER)

    # Create subfolder for Adsorbates if necessary
    Biblio_folder = JSON_FOLDER + "/Bibliography"
    if not os.path.exists(Biblio_folder):
        os.mkdir(Biblio_folder)

    # Generate a list of adsorbents from the MATDB API
    url = API_HOST + "/isodb/api/biblios.json"
    bibliography = json.loads(requests.get(url, headers=HEADERS).content)
    print(len(bibliography), "Bibliography Entries")

    # Extract each paper in full form
    for (biblio_count, biblio) in enumerate(bibliography):
        doi = biblio["DOI"]
        doi_stub = biblio["DOI"]
        for rule in doi_stub_rules:
            doi_stub = doi_stub.replace(rule["old"], rule["new"])
        url = API_HOST + "/isodb/api/biblio/" + doi + ".json"
        url = url.replace("%", "%25")  # make this substitution first
        url = url.replace("+", "%252B")
        try:
            biblio_data = json.loads(requests.get(url, headers=HEADERS).content)[
                0
            ]  # look at the API call here
            # pprint.pprint(biblio_data)
            # Write to JSON
            filename = doi_stub + ".json"
            json_writer(Biblio_folder + "/" + filename, biblio)
        except:
            print("ERROR: ", doi)
            print(url)
        # if biblio_count > 5: break
        if biblio_count % 100 == 0:
            time.sleep(5)  # slow down API calls to not overwhelm the server


@cli.command("git_log")
def git_log():
    """parse the git log"""
    print("parsing the git log")
    repo = git.Repo(SCRIPT_PATH)
    commits = list(repo.iter_commits("master", max_count=5))
    for commit in commits:
        print(commit.message)


def fix_gas_ID(input):
    output = copy.deepcopy(input)
    gas_name = input["name"].lower().replace(" ", "%20")
    url = API_HOST + "/isodb/api/gas/" + gas_name + ".json&k=dontrackmeplease"
    # Attempt to resolve the name using the ISODB API
    try:
        gas_info = json.loads(requests.get(url, headers=HEADERS).content)
        output["InChIKey"] = gas_info["InChIKey"]
        output["name"] = gas_info["name"]
        check = True
    except:
        check = False
    return output, check


def fix_material_ID(input):
    output = copy.deepcopy(input)
    material_name = input["name"].lower().replace("%", "%25").replace(" ", "%20")
    url = API_HOST + "/matdb/api/material/" + material_name + ".json&k=dontrackmeplease"
    # Attempt to resolve the name using the MATDB API
    try:
        material_info = json.loads(requests.get(url, headers=HEADERS).content)
        output["hashkey"] = material_info["hashkey"]
        output["name"] = material_info["name"]
        check = True
    except:
        check = False
    return output, check


def default_adsorption_units(input):
    # Generate units lookup tables from API
    url = API_HOST + "/isodb/api/default-adsorption-unit-lookup.json"
    default_units = json.loads(requests.get(url, headers=HEADERS).content)
    url = API_HOST + "/isodb/api/adsorption-unit-lookup.json"
    all_units = json.loads(requests.get(url, headers=HEADERS).content)
    # input -> ID -> output mapping
    ID = next(item for item in all_units if item["name"].lower() == input.lower())["id"]
    output = next(item for item in default_units if item["id"] == ID)["name"]
    return output


@cli.command("post_process")
@click.argument("filename", type=click.Path(exists=True), nargs=1)
def post_process(filename):
    with open(filename, mode="r") as infile:
        isotherm = json.load(infile)
    print("before")
    pprint.pprint(isotherm)
    # Check for adsorbate InChIKey(s)
    #  a. isotherm metadata
    adsorbates = isotherm["adsorbates"]
    for (i, adsorbate) in enumerate(adsorbates):
        if "InChIKey" not in adsorbate:
            # Correct the gas ID using the ISODB API
            adsorbate, check = fix_gas_ID(adsorbate)
            if not check:
                raise Exception("UNKNOWN ADSORBATE: ", adsorbate, filename)
            else:
                adsorbates[i] = adsorbate
        else:
            # Confirm that the InChIKey is in the ISODB
            url = API_HOST + "/isodb/api/gases.json"
            adsorbates_list = json.loads(requests.get(url, headers=HEADERS).content)
            adsorbate_inchikeys = [x["InChIKey"] for x in adsorbates_list]
            if adsorbate["InChIKey"] not in adsorbate_inchikeys:
                print("new inchikey, create upload file")
                # needs to include inchikey, name  <- double check this!!!!
                # Extract adsorbate dictionary as a new file
                filename = adsorbate["InChIKey"] + ".json"
                json_writer(filename, adsorbate)
    #  b. isotherm data points
    for point in isotherm["isotherm_data"]:
        for species in point["species_data"]:
            if "InChIKey" not in species:
                # Correct the gas ID
                adsorbate, check = fix_gas_ID({"name": species["name"]})
                if not check:
                    raise Exception("UNKNOWN ADSORBATE: ", adsorbate, filename)
                else:
                    species["InChIKey"] = adsorbate["InChIKey"]
                    del species["name"]
    # Check for adsorbent hashkey
    adsorbent = isotherm["adsorbent"]
    if "hashkey" not in adsorbent:
        # Correct the material ID
        material, check = fix_material_ID(adsorbent)
        if not check:
            raise Exception("UNKNOWN ADSORBENT: ", adsorbent, filename)
        else:
            adsorbent["hashkey"] = material["hashkey"]
            adsorbent["name"] = material["name"]
    # Convert pressure to bar units
    raw_units = isotherm["pressureUnits"]
    if raw_units == "RELATIVE":
        try:
            p_conversion = isotherm["saturationPressure"]
        except:
            raise Exception(
                "RELATIVE pressure units declared; must specify saturationPressure (in bar)"
            )
    else:
        try:
            p_conversion = pressure_units[raw_units]  # conversion from raw_units to bar
        except:
            raise Exception("Unknown pressure units: ", raw_units)
    try:
        log_scale = isotherm["log_scale"]
    except:
        log_scale = False
    for point in isotherm["isotherm_data"]:
        pressure_okay = True
        if log_scale:
            # Convert from log (assume base-10) to bar pressure
            try:
                point["pressure"] = (10.0 ** point["pressure"]) * p_conversion
            except:
                raise Exception(
                    "ERROR: unable to convert log-scale pressure: ", point["pressure"]
                )
        else:
            # Otherwise, just convert bar pressure
            point["pressure"] = point["pressure"] * p_conversion
    isotherm["pressureUnits"] = "bar"
    # Map the adsorptionUnits to the default value
    isotherm["adsorptionUnits"] = default_adsorption_units(isotherm["adsorptionUnits"])
    # Convert the tabular_data boolean variable to integer (SQL does not support boolean)
    if isotherm["tabular_data"] == True:
        isotherm["tabular_data"] = 1
    elif isotherm["tabular_data"] == False:
        isotherm["tabular_data"] = 0
    elif isotherm["tabular_data"] != 0 and isotherm["tabular_data"] != 1:
        raise ValidationError(
            "ERROR: 'tabular_data' field does not conform to either (0,1) or (False,True)"
        )

    # Trim out points with invalid pressure or adsorption
    new_points = []
    for point in isotherm["isotherm_data"]:
        yvalues = [species["adsorption"] for species in point["species_data"]]
        #  Include points with pressure > 0. or adsorption > 0.
        if point["pressure"] > 0.0 and min(yvalues) > 0.0:
            new_points.append(point)
    isotherm["isotherm_data"] = new_points
    # Clean up unnecessary keys
    for key in copy.copy(isotherm):
        if key not in canonical_keys:
            del isotherm[key]
    # We're finally done, output!
    isotherm["filename"] = "newfile.json"
    json_writer("newfile.json", isotherm)
    print("after")
    pprint.pprint(isotherm)


# To Do:
# Post-Process Script:
#   Do we want to deal with partial-pressure in the isotherm_data block ?  (appears in composition area)
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


def extract_names(string):
    if string.count(".") > 1:
        split_string = string.split(".", 1)
        given = split_string[0] + "."
        middle = split_string[1].lstrip()
    elif " " in string:
        # print 'spaces', string
        split_string = string.split(" ", 1)
        given = split_string[0]
        middle = split_string[1]
    else:
        given = string
        middle = None
    # Remove preceding dash from middle
    if middle != None and len(middle) > 0 and middle[0] == "-":
        middle = middle.split("-", 1)[1]
    return {"given": given, "middle": middle}


def fix_journal(journal_in):
    # Point Corrections for journals with inconsistent naming",
    if journal_in == "angewandte chemie international edition":
        output = "angewandte chemie-international edition"
    elif journal_in == "zeitschrift für anorganische und allgemeine chemie":
        output = "zeitschrift fur anorganische und allgemeine chemie"
    elif journal_in == "the canadian journal of chemical engineering":
        output = "canadian journal of chemical engineering"
    elif journal_in == "applied catalysis a: general":
        output = "applied catalysis a-general"
    elif journal_in == "applied catalysis b: environmental":
        output = "applied catalysis b-environmental"
    elif journal_in == "journal of molecular catalysis a: chemical":
        output = "journal of molecular catalysis a-chemical"
    elif journal_in == "energy environ sci":
        output = "energy and environmental science"
    elif journal_in == "fullerenes, nanotubes and carbon nanostructures":
        output = "fullerenes nanotubes and carbon nanostructures"
    elif journal_in == "environmental science: nano":
        output = "environmental science-nano"
    elif journal_in == "chimia international journal for chemistry":
        output = "chimia"
    elif journal_in == "journal of chemical technology & biotechnology":
        output = "Journal of Chemical Technology and Biotechnology"
    elif (
        journal_in == "colloids and surfaces a: physicochemical and engineering aspects"
    ):
        output = "Colloids and Surfaces A-Physicochemical and Engineering Aspects"
    elif journal_in == "journal of environmental sciences":
        output = "Journal of Environmental Sciences-China"
    else:
        output = journal_in
    return output


@cli.command("generate_bibliography")
@click.argument("folder", type=click.Path(exists=True), nargs=1)
def generate_bibliography(folder):

    # Generate a list of isotherms to process
    if folder[-1] != "/":
        folder += "/"
    filenames = glob.glob(folder + "*")
    filenamess = [x for x in filenames if "isotherm" in x or "Isotherm" in x]
    # Extract the unique DOIs
    DOIs = []
    for filename in filenames:
        with open(filename, mode="r") as handle:
            isotherm = json.load(handle)
        if isotherm["DOI"].lower() not in [x.lower() for x in DOIs]:
            DOIs.append(isotherm["DOI"])
    # print(DOIs)

    for doi in DOIs:
        # Pull bibliographic metadata from the dx.doi.org API
        try:
            url = "https://doi.org/" + doi
            bib_info = json.loads(requests.get(url, headers=HEADERS).content)
        except:
            raise RuntimeError("ERROR: DOI problem for:" + doi)
        title = bib_info["title"].encode(TEXTENCODE).decode()
        journal = (
            bib_info["container-title"]
            .replace(".", "")
            .encode(TEXTENCODE)
            .lower()
            .decode()
        )
        journal = fix_journal(journal)
        year = int(bib_info["issued"]["date-parts"][0][0])
        # -----------------------------
        # Match Journal Name/Abbreviation to existing lookup
        url = API_HOST + "/isodb/api/journals-lookup.json"
        journals = json.loads(requests.get(url, headers=HEADERS).content)
        if journal in [x["name"].lower() for x in journals]:
            # Attempt to match journal by name (lower case)
            index = [x["name"].lower() for x in journals].index(journal)
            journal = {"journal_id": journals[index]["id"]}
            journal["name"] = journals[index]["name"]
        elif journal in [x["abbreviation"].lower().replace(".", "") for x in journals]:
            # attempt to match journal by abbreviation (lower case, strip out periods)
            index = [
                x["abbreviation"].lower().replace(".", "") for x in journals
            ].index(journal.replace(".", ""))
            journal = {"journal_id": journals[index]["id"]}
            journal["abbreviation"] = journals[index]["abbreviation"]
        else:
            raise Exception("Unknown Journal: ", journal)
        # ------------------------------
        # Parse the author list
        authors = []
        for (i, author) in enumerate(bib_info["author"]):
            block = {}
            block["order_id"] = i + 1
            block["family_name"] = unicodedata.normalize("NFKC", author["family"])
            try:
                given_names = extract_names(author["given"])
                block["given_name"] = unicodedata.normalize(
                    "NFKC", given_names["given"]
                )
            except:
                raise Exception(
                    "Error parsing author block: " + author + "\n for DOI: " + doi
                )
            if given_names["middle"] != None:
                block["middle_name"] = unicodedata.normalize(
                    "NFKC", given_names["middle"]
                )
                if "ORCID" in author:
                    block["orc_id"] = author["ORCID"].replace("http://orcid.org/", "")
            authors.append(block)

        # Collect metadata from the isotherms
        adsorbates = []
        adsorbents = []
        temperatures = []
        categories = []
        min_pressure = 1.0e10  # initialize this absurdly
        max_pressure = -1.0e10  # initialize this absurdly
        isotherms = []

        for filename in filenames:
            with open(filename, mode="r") as handle:
                isotherm = json.load(handle)
            if isotherm["DOI"].lower() == doi.lower():

                adsorbents.append(str(isotherm["adsorbent"]["hashkey"]))
                if str(isotherm["category"]) != "":
                    categories.append(str(isotherm["category"]))
                temperatures.append(int(isotherm["temperature"]))
                for adsorbate in isotherm["adsorbates"]:
                    adsorbates.append(adsorbate["InChIKey"])
                for point in isotherm["isotherm_data"]:
                    min_pressure = min(min_pressure, point["pressure"])
                    max_pressure = max(max_pressure, point["pressure"])

                # Correction to pressure range
                if min_pressure < 0.0:
                    min_pressure = 0.00
                if max_pressure > 1000.0:
                    max_pressure = 1000.00

                isotherms.append(filename.split("/")[-1])

        # Reduce redundant lists to unique lists and convert to dictionaries
        adsorbents = [{"hashkey": x} for x in sorted(list(set(adsorbents)))]
        categories = [{"name": x} for x in sorted(list(set(categories)))]
        temperatures = list(set(temperatures))
        adsorbates = [{"InChIKey": x} for x in sorted(list(set(adsorbates)))]
        # This is an odd sorting algorithm, but is necessary to immitate the API
        #  Sort is case insensitive, but preserves filename case
        isotherms = sorted(
            [x.replace(".json", "") for x in isotherms], key=str.casefold
        )
        isotherms = [{"filename": x} for x in isotherms]

        # Build the JSON Structure
        biblio = {}
        biblio["DOI"] = doi
        biblio["categories"] = categories
        biblio["adsorbates"] = adsorbates
        biblio["adsorbents"] = adsorbents
        biblio["temperature"] = temperatures
        biblio["pressure_min"] = float("{0:.2f}".format(min_pressure))
        biblio["pressure_max"] = float("{0:.2f}".format(max_pressure))
        biblio["title"] = title
        biblio["year"] = year
        biblio["journal"] = journal
        biblio["authors"] = authors
        biblio["isotherms"] = isotherms

        # Write to disk
        doi_stub = doi
        for rule in doi_stub_rules:
            doi_stub = doi_stub.replace(rule["old"], rule["new"])

        json_writer(
            doi_stub + ".json", biblio
        )  # this creates the upload file for ISODB
        # pprint.pprint(biblio)

        # Simulate the ISODB API
        biblio_API = copy.deepcopy(biblio)
        biblio_API["journal"] = biblio_API["journal"]["name"]
        biblio_API["categories"] = [x["name"] for x in biblio_API["categories"]]
        biblio_API["pressures"] = [min_pressure, max_pressure]
        del biblio_API["pressure_min"]
        del biblio_API["pressure_max"]
        biblio_API["temperatures"] = biblio_API.pop("temperature")
        # Simplify Authors
        authors = []
        for author in biblio_API["authors"]:
            name = []
            for key in ["given_name", "middle_name", "family_name"]:
                if key in author:
                    name.append(author[key])
            name = " ".join(name)
            authors.append(name)
        biblio_API["authors"] = authors
        # Adsorbates List
        biblio_API["adsorbateGas"] = []
        for adsorbate in biblio_API["adsorbates"]:
            # Look up name associated with InChIKey
            url = (
                API_HOST
                + "/isodb/api/gas/"
                + adsorbate["InChIKey"]
                + ".json&k=dontrackmeplease"
            )
            info = json.loads(requests.get(url, headers=HEADERS).content)
            adsorbate["name"] = info["name"]
            biblio_API["adsorbateGas"].append(info["name"])
        # Adsorbents List
        biblio_API["adsorbentMaterial"] = []
        for adsorbent in biblio_API["adsorbents"]:
            # Look up name associated with hashkey
            url = (
                API_HOST
                + "/matdb/api/material/"
                + adsorbent["hashkey"]
                + ".json&k=dontrackmeplease"
            )
            info = json.loads(requests.get(url, headers=HEADERS).content)
            adsorbent["name"] = info["name"]
            biblio_API["adsorbentMaterial"].append(info["name"])
        json_writer(
            doi_stub + ".json.API", biblio_API
        )  # this creates the ISODB Library file


# To-Do for Bibliography Generator
#   New journals - how to handle


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
