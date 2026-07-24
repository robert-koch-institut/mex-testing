# MEx testing

Assets, tools and services for mocking and testing MEx packages.

[![cookiecutter](https://github.com/robert-koch-institut/mex-testing/actions/workflows/cookiecutter.yml/badge.svg)](https://github.com/robert-koch-institut/mex-template)
[![cve-scan](https://github.com/robert-koch-institut/mex-testing/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-testing/actions/workflows/cve-scan.yml)
[![documentation](https://github.com/robert-koch-institut/mex-testing/actions/workflows/documentation.yml/badge.svg)](https://robert-koch-institut.github.io/mex-testing)
[![linting](https://github.com/robert-koch-institut/mex-testing/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-testing/actions/workflows/linting.yml)
[![opencode](https://github.com/robert-koch-institut/mex-testing/actions/workflows/opencode.yml/badge.svg)](https://gitlab.opencode.de/robert-koch-institut/mex/mex-testing)
[![testing](https://github.com/robert-koch-institut/mex-testing/actions/workflows/testing.yml/badge.svg)](https://github.com/robert-koch-institut/mex-testing/actions/workflows/testing.yml)

## Project

The Metadata Exchange (MEx) project is committed to improve the retrieval of RKI
research data and projects. How? By focusing on metadata: instead of providing the
actual research data directly, the MEx metadata catalog captures descriptive information
about research data and activities. On this basis, we want to make the data FAIR[^1] so
that it can be shared with others.

Via MEx, metadata will be made findable, accessible and shareable, as well as available
for further research. The goal is to get an overview of what research data is available,
understand its context, and know what needs to be considered for subsequent use.

RKI cooperated with D4L data4life gGmbH for a pilot phase where the vision of a
FAIR metadata catalog was explored and concepts and prototypes were developed.
The partnership has ended with the successful conclusion of the pilot phase.

After an internal launch, the metadata will also be made publicly available and thus be
available to external researchers as well as the interested (professional) public to
find research data from the RKI.

For further details, please consult our
[project page](https://www.rki.de/DE/Aktuelles/Publikationen/Forschungsdaten/MEx/metadata-exchange-plattform-mex-node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

**Contact** \
For more information, please feel free to email us at [mex@rki.de](mailto:mex@rki.de).

### Publisher

**Robert Koch-Institut** \
Nordufer 20 \
13353 Berlin \
Germany

## Package

This package provides utilities, test data, and mock services for the MEx ecosystem
(mex-common, mex-backend, mex-editor, and related services). It helps with running
services without access to internal infrastructure as well as with implementing and
running integration tests.

## License

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.

## Development

### Installation

- install python on your system
- on unix, run `make install`
- on windows, run `.\mex.bat install`

### Linting and testing

- run all linters with `make lint` or `.\mex.bat lint`
- run unit and integration tests with `make test` or `.\mex.bat test`
- run just the unit tests with `make unit` or `.\mex.bat unit`

### Updating dependencies

- update boilerplate files with `cruft update`
- update global requirements in `requirements.txt` manually
- update git hooks with `pre-commit autoupdate`
- update package dependencies using `uv sync --upgrade`
- update github actions in `.github/workflows/*.yml` manually

### Creating release

- run `mex release RULE` to release a new version where RULE determines which part of
  the version to update and is one of `major`, `minor`, `patch`.

### Container workflow

- build image with `make image`
- run directly using docker `make run`
- start with docker compose `make start`

### Container verification

Images released to GHCR are signed using [cosign](https://github.com/sigstore/cosign).

To verify an image manually:
`cosign verify --certificate-identity-regexp "https://github.com/robert-koch-institut/mex-testing/.github/workflows/release.yml@refs/heads/main" --certificate-oidc-issuer "https://token.actions.githubusercontent.com" ghcr.io/robert-koch-institut/mex-testing:<tag>`

## HTTP test server

The testing service ships a simple HTTP server for mocking external systems during
integration tests.

### Endpoints

#### GET/POST `/v0/{path-to-file}`

- Serves files from `TestingSettings.http_server_test_data_directory`
- Maps `{path-to-file}` to files in the test data directory
- Uses file extension to determine mimetype
- Returns 404 if no matching file or multiple files found

**Example:**

- File at `assets/extractor1/data.json`
- Served via `/v0/extractor1/data`

#### HEAD `/v0/{path-to-file}`

- Always returns HTTP 200 OK status

#### POST `/v0/datscha_web/login.php`

- Custom endpoint for datscha web login
- Returns redirect to "verzeichnis.php"

### Directory structure

```
assets/
├── extractor1/
│   └── file1.json       # Access via /extractor1/file1
├── extractor2/
│   ├── file.xml         # Access via /extractor2/file
│   └── file.csv         # Access via /extractor2/file
```

### Configuration

- `MEX_TESTING_HTTP_SERVER_DATA_DIRECTORY`: Root directory for test data (default: assets dir)
- `MEX_TESTING_HTTP_SERVER_HOST`: Host (default: `localhost`)
- `MEX_TESTING_HTTP_SERVER_PORT`: Port (default: `8088`)
- `MEX_TESTING_HTTP_SERVER_ROOT_PATH`: Root path for the server

### Custom endpoints

Add new endpoints by extending the API router in `mex/testing/main.py`:

```python
@router.post("/custom/path")
def custom_endpoint() -> Response:
    return Response(content="custom response")
```

## Commands

- run `uv run {command} --help` to print instructions
- run `uv run {command} --debug` for interactive debugging

### testing

- `testing` starts the testing service
