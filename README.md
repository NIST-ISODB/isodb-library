# NIST/ARPA-E Database of Novel and Emerging Adsorbent Materials

The [NIST/ARPA-E Database of Novel and Emerging Adsorbent Materials](https://adsorption.nist.gov/isodb) is a free, web-based catalog of adsorbent materials and measured adsorption properties of numerous materials obtained from article entries from the scientific literature.
The database also contains adsorption isotherms digitized from the cataloged articles, which can be compared visually online in the web application, analyzed online with available tools, or exported for offline analysis.

This is the official Github mirror of the database, providing a new way of submitting new isotherms, corrections, and updates.

## Requirements

Repo relies on isodbtools, a toolset developed by NIST for management of adsorption data.

Install via:

```
pip install git+https://github.com/NIST-ISODB/isodbtools.git#egg=isodbtools
```

## Contributing

Contributions of new isotherms, corrections and updates are highly welcome!

#### Contributing new isotherms

Use the [Isotherm digitizer web application](http://digitizer.matscreen.com/digitizer)

#### Contributing a correction

Individual corrections can be contributed directly through the Github web site:

 1. Use the Github search bar to search for the isotherm filename, e.g. `10.1002adem.200500223.isotherm2`
 2. Click on the file
 3. Click on the "pen" symbol to propose changes.
    This will fork the database in your Github accunt.
 4. Click on "Create pull request"

#### Contributing bulk updates

Bulk updates (both new isotherms and corrections) are easier done with a local copy of the repository.

 1. Fork this repository
 2. Clone the repository locally
 3. Enable pre-commit hooks
    ```
    pip install -r .github/requirements.txt
    pre-commit install
    ```
 4. Commit your changes
 5. Make a pull request

Note: The pre-commit hooks will auto-format your contribution and perform basic consistency checks.
