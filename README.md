# NIST/ARPA-E Database of Novel and Emerging Adsorbent Materials

The [NIST/ARPA-E Database of Novel and Emerging Adsorbent Materials](https://adsorption.nist.gov/isodb) is a free, web-based catalog of adsorbent materials and measured adsorption properties of numerous materials obtained from article entries from the scientific literature.
The database also contains adsorption isotherms digitized from the cataloged articles, which can be compared visually online in the web application, analyzed online with available tools, or exported for offline analysis.

This is the official Github mirror of the database, providing a new way of submitting new isotherms, corrections, and updates.

## Contributing

Contributions of new isotherms, corrections and updates are highly welcome!

#### Contributing a new isotherm

Use the [Isotherm digitizer web application]() (under development)

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
