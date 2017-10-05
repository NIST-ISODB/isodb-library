# NIST/ARPA-E Database of Novel and Emerging Adsorbent Materials
## Historical Snapshots of the full output of the NIST-ISODB Application Programming Interface (API)

**CONTEXTUAL NOTE:** The [NIST-ISODB](https://adsorption.nist.gov/isodb/index.php#apis) was upgraded to version 2.0 on 2017-10-05. Version 1.0 supported only single-component isotherms and was fundamentally incompatible with version 2.0, which fully supports multicomponent isotherms.

The commits to this branch of the isodb-library repository contain the full history of the output of the NIST-ISODB API from 2017-10-05 to 2020-08-11.

Each commit in the [`historical`](https://github.com/NIST-ISODB/isodb-library/tree/historical) branch of this repo is a snapshot of the full output of the NIST-ISODB API in JSON format as of the date noted in the commit. It includes API output for all:
1. Adsorbate species,
1. Adsorbent materials,
1. Bibliographic entries,
1. Isotherms
in NIST-ISODB.

The repository is structured identical to the [`master`](https://github.com/NIST-ISODB/isodb-library/tree/master) branch of the isodb-library repository, as of 2020-12-22:
1. Adsorbate JSON files in Library/Adsorbates
1. Adsorbent JSON files in Library/Adsorbents
1. Bibliography JSON files in Library/Bibliography
1. Isotherm JSON files, organized by source DOI, in Library/DOI_stub

The `DOI_stub` is generated from the source DOI by using the `doi_stub_generator` function in the https://github.com/NIST-ISODB/isodbtools repository:

```DOI_stub = isodbtools.doi_stub_generator(DOI)```

