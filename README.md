![build status](https://code-int.ornl.gov/daacutils/update_metadata_curl_files/badges/master/build.svg)
![coverage](https://code-int.ornl.gov/daacutils/update_metadata_curl_files/badges/master/coverage.svg?job=test)

## CONTENTS OF THIS FILE

* [Introduction](#INTRODUCTION)
* [Usage](#USAGE)
* [Requirements](#REQUIREMENTS)

## INTRODUCTION

Utility for creating metadata curl scripts by querying https://cmr.earthdata.nasa.gov.

This script does the following:
1) Download a list of all collections associated with the given data center and project from CMR.
2) Download a list of all granules for each collection from CMR.
3) Create a metadata.curl file in the output directory for each collection.
   A metadata.curl file contains curl commands to download each granule of the collection.

The raw output of each CMR query in steps 1 & 2 is stored in the temporary directory.
This behaviour can be disabled with command line flags to check for changes on the CMR.

## USAGE

`update_metadata_curl_files.py` can be run from the command line or as a Python module.

### COMMAND LINE USAGE

The basic syntax is the following:

```
python update_metadata_curl_files.py [OPTIONS] data_center project
```

* `data_center` can be the name of a data center to query or `all` to return collections from all data centers.
* `project` can be the name of a project to query or `all` to return collections from all projects.

For a list of valid options run `update_metadata_curl_files.py` with the `-h` option:
```
python update_metadata_curl_files.py -h
```

### COMMAND LINE USAGE EXAMPLES

To create metadata CURL files for all collections of the ABoVE project from the ORNL DAAC data center, run the following command:

```
python update_metadata_curl_files.py ORNL_DAAC ABoVE
```

To create metadata CURL files for all collections of any project from the ORNL DAAC data center, run the following command:

```
python update_metadata_curl_files.py ORNL_DAAC all
```

By default, `update_metadata_curl_files.py` caches all queries as JSON files in the `/tmp` directory. Therefore added-, removed- or changed collections or granules will not be updated unless the `--update-collections` and `--update-granules` flags are set.

To update previously downloaded metadata CURL files to cover all granules of all collections of the ABoVE project from the ORNL DAAC data center, run the following command:

```
python update_metadata_curl_files.py ORNL_DAAC all --update-collections --update-granules
```

### PYTHON MODULE USAGE

`update_metadata_curl_files.py` can be run from Python code by importing the package and calling the `main` function. The `main` function has the following parameters:

* `data_center (str)` The name of a data center to query or `all` to return collections from all data centers.
* `project (str)` The name of a project to query or `all` to return collections from all projects.
* `update_collections (bool)` If true, ignores cached collections.
* `update_granules (bool)` If true, ignores cached granules.
* `events (Events, optional)` A user provided class for customized logging. Defaults to `PrintEvents()`.
* `temp_dir (str, optional)` Directory for storing cached CMR queries in JSON format. Defaults to "./tmp".
* `output_dir (str, optional)` Directory for storing generated metadata CURL files. Defaults to "./out".
* `concept_format (str, optional)` Response format for granule downloads. This affects the `Accept` header and output file extension of the generated curl commands. Defaults to "json".

### PYTHON MODULE USAGE EXAMPLES

To create metadata CURL files for all collections of the ABoVE project from the ORNL DAAC data center, run the following Python code:

```Python
import update_metadata_curl_files as umcf

umcf.main(
    data_center="ORNL_DAAC",
    project="ABoVE",
    update_collections=False,
    update_granules=False,
    events=umcf.PrintEvents()
)
```

## REQUIREMENTS

`update_metadata_curl_files.py` requires Python 2 or above. See [requirements.txt](requirements.txt) for a list of required Python packages. It has been tested with Python 2.7, 3.6 and 3.7.