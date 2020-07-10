#!/usr/bin/env python

import os
import pprint
import json
import requests
import unicodedata
import time
import copy
import click
import git

# Global Variables
API_HOST = "https://adsorption.nist.gov"
HEADERS = {'Accept': 'application/citeproc+json'} # JSON Headers

SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
ROOT_DIR = os.getcwd()
DOI_MAPPING_PATH = os.path.join(ROOT_DIR, "DOI_mapping.csv")
JSON_FOLDER = os.path.join(ROOT_DIR, "Library")

# Character Substitution Rules for Converting the DOI to a stub
doi_stub_rules = [
    {"old": "/", "new": "-"},
    {"old": "(", "new": ""},
    {"old": ")", "new": ""},
    {"old": ":", "new": ""},
    {"old": ":", "new": ""},
    {"old": " ", "new": ""},
    {"old": "+", "new": "plus"},
    {"old": "-", "new": ""}
]

# Pressure Conversions (to bar units)
pressure_units = {
        'bar': 1.0 ,
        'Pa': 1.0e-05,
        'kPa': 1.0e-02,
        'MPa': 10.0 ,
        'atm': 1.01325e0,
        'mmHg': 1.333223684e-03,
        'Torr': 1.333223684e-03,
        'psi': 6.8947572932e-02,
        'mbar': 1.0e-03
    }

# Canonical Keys for Isotherm JSON (required keys for ISODB)
canonical_keys = [
    "DOI", "adsorbates", "adsorbent", "adsorptionUnits", "articleSource", "category", "compositionType",
    "concentrationUnits", "date", "digitizer", "filename", "isotherm_data", "isotherm_type", "pressureUnits",
    "tabular_data", "temperature"
]

# Wrapper function for JSON writes to ensure consistency in formatting
def json_writer(filename,data):
    """Format JSON according to ISODB specs"""
    with open(filename,mode='w') as output:
        json.dump(data, output,
                  ensure_ascii=False,sort_keys=True,indent=4) #formatting rules
        output.write('\n') #new line at EOF
        
@click.group()
def cli():
    pass

@cli.command("clean_json")
@click.argument("filename", type=click.Path(exists=True), nargs=1)
def clean_json(filename):
    """Read in JSON and output according to ISODB specs"""
    print('operate on filename: ', filename)
    with open(filename,mode='r') as infile:
        isotherm_data = json.load(infile)
    os.rename(filename,filename+'.bak')
    json_writer(filename,isotherm_data)
    os.remove(filename+'.bak')

@cli.command("download_isotherm")
@click.argument("isotherm", nargs=1)
def download_isotherm(isotherm):
    """Download a specific isotherm from the ISODB and format to ISODB specs"""
    if isotherm[-5:] != '.json': isotherm += '.json'
    print('Downloading Isotherm: ', isotherm)
    url = API_HOST + '/isodb/api/isotherm/'+isotherm
    isotherm_data = json.loads(requests.get(url, headers=HEADERS).content)
    json_writer(isotherm,isotherm_data)
    

@cli.command("regenerate_library")
def regenerate_library():
    """Generate the entire ISODB library from the API"""
    # Create the JSON Library folder if necessary
    if not os.path.exists(JSON_FOLDER):
        os.mkdir(JSON_FOLDER)
                
    #Generate a DOI list from the ISODB API
    url = API_HOST+"/isodb/api/biblio.json"
    bibliography = json.loads(requests.get(url, headers=HEADERS).content)
    print(len(bibliography), 'Bibliography Entries')

    #Count isotherms for DOIs in the database
    url = API_HOST+"/isodb/api/isotherms.json"
    isotherms_list = json.loads(requests.get(url, headers=HEADERS).content)
    isotherm_count = {}
    for isotherm in isotherms_list:
        doi = isotherm["DOI"].lower()
        if doi not in isotherm_count:
            isotherm_count[doi] = 1
        else:
            isotherm_count[doi] += 1
    print(len(isotherms_list), 'Isotherm Files')

    #Create a CSV file with the DOI -> folder mapping
    DOI_mapping = open(DOI_MAPPING_PATH,mode='w')
    DOI_mapping.write( 'DOI,  "DOI Stub"\n' )

    #Download and Organize the Isotherms
    article_count = 0
    for article in bibliography:
        #print(article["isotherms"])
    
        # Shorten the DOI according to rules specified in global variables
        doi = article["DOI"]
        doi_stub = article["DOI"]
        for rule in doi_stub_rules:
            doi_stub = doi_stub.replace(rule["old"],rule["new"])
    
        num_isotherms = len(article["isotherms"])
        #print(doi, doi_stub, num_isotherms)
    
        # Download the isotherms
        if num_isotherms > 0:
            article_count += 1
            DOI_FOLDER = os.path.join(JSON_FOLDER, doi_stub)
            #print(DOI_FOLDER)
            if not os.path.exists(DOI_FOLDER):
                os.mkdir(DOI_FOLDER)
            DOI_mapping.write(doi+', '+doi_stub+'\n')
            
            for isotherm in article["isotherms"]:
                url = API_HOST + '/isodb/api/isotherm/'+isotherm["filename"]+'.json'
                isotherm_JSON = json.loads(requests.get(url, headers=HEADERS).content)
                #print(json.dumps(isotherm_JSON, sort_keys=True))
                filename = os.path.join(DOI_FOLDER, isotherm["filename"]+".json")
                #print(filename)
                json_writer(filename,isotherm_JSON)
                #break
            print(doi, 'Finished')

            #break
            
        #if article_count > 50: break
        if article_count%10 == 0: time.sleep(5) #slow down API calls to not overwhelm the server
        #break

    print(article_count, 'Objects with Isotherms')
    DOI_mapping.close()

@cli.command("git_log")
def git_log():
    """parse the git log"""
    print('parsing the git log')
    repo = git.Repo(SCRIPT_PATH)
    commits = list(repo.iter_commits("master", max_count=5))
    for commit in commits:
        print(commit.message)


def fix_gas_ID(input):
    output = copy.deepcopy(input)
    gas_name = input["name"].lower().replace(' ','%20')
    url = API_HOST+"/isodb/api/gas/"+gas_name+".json&k=dontrackmeplease"
    #Attempt to resolve the name using the ISODB API
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
    material_name = input["name"].lower().replace('%','%25').replace(' ','%20')
    print(material_name)
    url = API_HOST+"/matdb/api/material/"+material_name+".json&k=dontrackmeplease"
    print(url)
    #Attempt to resolve the name using the MATDB API
    try:
        material_info = json.loads(requests.get(url, headers=HEADERS).content)
        output["hashkey"] = material_info["hashkey"]
        output["name"] = material_info["name"]
        check = True
    except:
        check = False
    return output, check
        

@cli.command("post_process")
@click.argument("filename", type=click.Path(exists=True), nargs=1)
def post_process(filename):
    with open(filename,mode='r') as infile:
        isotherm = json.load(infile)
    print('before')
    pprint.pprint(isotherm)
    # Check for adsorbate InChIKey(s)
    #  a. isotherm metadata
    adsorbates = isotherm["adsorbates"]
    for (i,adsorbate) in enumerate(adsorbates):
        if "InChIKey" not in adsorbate:
            #Correct the gas ID
            adsorbate, check = fix_gas_ID(adsorbate)
            if not check:
                raise Exception('UNKNOWN ADSORBATE: ', adsorbate, filename)
            else:
                adsorbates[i] = adsorbate
    #  b. isotherm data points
    for point in isotherm["isotherm_data"]:
        for species in point["species_data"]:
            if "InChIKey" not in species:
                #Correct the gas ID
                adsorbate, check = fix_gas_ID({'name': species["name"]})
                if not check:
                    raise Exception('UNKNOWN ADSORBATE: ', adsorbate, filename)
                else:
                    species["InChIKey"] = adsorbate["InChIKey"]
                    del species["name"]
    # Check for adsorbent hashkey
    adsorbent = isotherm["adsorbent"]
    if "hashkey" not in adsorbent:
        #Correct the material ID
        material, check = fix_material_ID(adsorbent)
        if not check:
            raise Exception('UNKNOWN ADSORBENT: ', adsorbent, filename)
        else:
            adsorbent["hashkey"] = material["hashkey"]
            adsorbent["name"] = material["name"]
    # Convert pressure to bar units
    raw_units = isotherm["pressureUnits"]
    if raw_units == 'RELATIVE':
        try:
            p_conversion = isotherm["saturationPressure"]
        except:
            raise Exception("RELATIVE pressure units declared; must specify saturationPressure (in bar)")
    else:
        try:
            p_conversion = pressure_units[raw_units] #conversion from raw_units to bar
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
                point["pressure"] = (10.**point["pressure"])*p_conversion
            except:
                raise Exception("ERROR: unable to convert log-scale pressure: ", point["pressure"])
        else:
            # Otherwise, just convert bar pressure
            point["pressure"] = point["pressure"]*p_conversion
    isotherm["pressureUnits"] = 'bar'
    # Trim out points with invalid pressure or adsorption
    new_points = []
    for point in isotherm["isotherm_data"]:
        yvalues = [ species["adsorption"] for species in point["species_data"] ]
        #  Include points with pressure > 0. or adsorption > 0.
        if point["pressure"] > 0. and min(yvalues) > 0.: new_points.append(point)
    isotherm["isotherm_data"] = new_points
    # Clean up unnecessary keys
    for key in copy.copy(isotherm):
        if key not in canonical_keys: del isotherm[key]    
    # We're finally done, output!
    isotherm["filename"] = "newfile.json"
    json_writer("newfile.json", isotherm)
    print('after')
    pprint.pprint(isotherm)
    

#To Do:
# Post-Process Script:
#   Do we want to deal with partial-pressure in the isotherm_data block ?  (appears in composition area)
#     DWS: inclined to not error check this block as it requires expert knowledge to compose
#   Handling of new adsorbent materials
#     Digitizer should include option to specify new adsorbent metadata
#   Handling of new adsorbates
#     Digitizer should include option to specify new adsorbate metadata
        
if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
