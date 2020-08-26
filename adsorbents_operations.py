import os
import pprint
import json
import requests
import unicodedata
import time
import copy
import glob

from config import *


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
