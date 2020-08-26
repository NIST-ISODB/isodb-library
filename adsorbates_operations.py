import os
import pprint
import json
import requests
import unicodedata
import time
import copy
import glob

from config import *


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
