"""
Utility for creating metadata curl scripts by querying https://cmr.earthdata.nasa.gov.

This script does the following:
1) Download a list of all collections associated with the given data center and project from CMR.
2) Download a list of all granules for each collection from CMR.
3) Create a metadata.curl file in the output directory for each collection.
   A metadata.curl file contains curl commands to download each granule of the collection.

The raw output of each CMR query in steps 1 & 2 is stored in the temporary directory.
This behaviour can be disabled with command line flags to check for changes on the CMR.

Written 10/2018 by S. Klaassen
"""

from __future__ import print_function
from argparse import ArgumentParser, RawTextHelpFormatter
import json
import math
import os.path
import requests

TEMP_DIR = "./tmp" # The directory, used to store all data retrieved from the CMR search API in JSON files
OUTPUT_DIR = "./out" # The directory, used to store all generated metadata in cURL files
QUERY_PAGE_SIZE = 2000 # The page size for CMR search results

def is_cached(what, temp_dir, **params):
    """Check if query results are cached in the `temp_dir` directory.

    This function checks the existance of a JSON file with previously downloaded CMR query results in the `temp_dir` directory.
    
    Args:
        what (String): The type of data to find
        temp_dir (String): The directory containing cached query results
        params (String): Search criteria and parameter options
    
    Returns:
        boolean: True, if cached results were found
    """

    filename = os.path.join(temp_dir, "{}_{}.json".format(what, '_'.join(params.values())))

    return os.path.exists(filename)

def retrieve_cached(what, temp_dir, **params):
    """Retrieve cached query results from the `temp_dir` directory.

    This function retrieves previously downloaded CMR query results from a JSON file in the `temp_dir` directory.
    
    Args:
        what (String): The type of data to find
        temp_dir (String): The directory containing cached query results
        params (String): Search criteria and parameter options
    
    Returns:
        dict: JSON response content
    """

    filename = os.path.join(temp_dir, "{}_{}.json".format(what, '_'.join(params.values())))

    with open(filename, "r") as f:
        return json.loads(f.read())

def download_from_cmr(what, temp_dir, **params):
    """Issue a search query to CMR and return a dict of the JSON response

    For documentation on what can be searched for on the CMR, refer to
    https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#collection-search-by-parameters
    (Parameters to this function correspond the chapter: "Find `what` by `params`").

    Results are stored in a JSON file in the `temp_dir` directory.
    Subsequent searches will return stored results, if available.
    
    Args:
        what (String): The type of data to find
        temp_dir (String): The directory containing cached query results
        params (String): Search criteria and parameter options
    
    Returns:
        dict: JSON response content
    """

    filename = os.path.join(temp_dir, "{}_{}.json".format(what, '_'.join(params.values())))

    # Query first page of search results
    headers = { "Accept": "application/json" }
    params["page_size"] = QUERY_PAGE_SIZE
    params["scroll"] = 'true'
    response = requests.get("https://cmr.earthdata.nasa.gov/search/" + what, params=params, headers=headers)
    num_entries = int(response.headers['CMR-Hits'])
    headers["CMR-Scroll-Id"] = response.headers['CMR-Scroll-Id']
    json_response = response.json()

    # Query remaining pages
    for _ in range(int(math.ceil(num_entries / QUERY_PAGE_SIZE) - 1)):
        response = requests.get("https://cmr.earthdata.nasa.gov/search/" + what, params=params, headers=headers)
        json_response_page = response.json()
        json_response['feed']['entry'] += json_response_page['feed']['entry'] # Append entries of this page to json_response

    # Save results to JSON file
    with open(filename, "w") as f:
        f.write(json.dumps(json_response, indent=4))

    return json_response

class Events(object):
    def collections_download_starting(self):
        pass
    def collections_download_cached(self):
        pass
    def collections_download_succeeded(self, collections):
        pass
    def collections_download_failed(self, err):
        pass
    def collections_download_cached_failed(self, err):
        pass

    def granules_download_starting(self, collection, dataset_name):
        pass
    def granules_download_cached(self, collection, dataset_name):
        pass
    def granules_download_succeeded(self, collection, dataset_name, granules):
        pass
    def granules_download_failed(self, collection, dataset_name, err):
        pass
    def granules_download_cached_failed(self, collection, dataset_name, err):
        pass

    def writing_curl_file_starting(self, collection, dataset_name, granules):
        pass
    def writing_curl_file_succeeded(self, collection, dataset_name, granules, filename):
        pass
    def writing_curl_file_failed(self, collection, dataset_name, granules, err):
        pass

class PrintEvents(Events):
    def collections_download_starting(self):
        print("downloading collections ... ", end='')
    def collections_download_cached(self):
        print("retrieving cached collections ... ", end='')
    def collections_download_succeeded(self, collections):
        print("got", len(collections), "collections")
    def collections_download_failed(self, err):
        print("raised", repr(err))
    def collections_download_cached_failed(self, err):
        print("raised", repr(err))

    def granules_download_starting(self, collection, dataset_name):
        print("downloading granules for dataset", dataset_name, "... ", end='')
    def granules_download_cached(self, collection, dataset_name):
        print("retrieving cached granules for dataset", dataset_name, "... ", end='')
    def granules_download_succeeded(self, collection, dataset_name, granules):
        print("got", len(granules), "granules")
    def granules_download_failed(self, collection, dataset_name, err):
        print("raised", repr(err))
    def granules_download_cached_failed(self, collection, dataset_name, err):
        print("raised", repr(err))

    def writing_curl_file_starting(self, collection, dataset_name, granules):
        print("writing metadata.curl file for dataset", dataset_name, "... ", end='')
    def writing_curl_file_succeeded(self, collection, dataset_name, granules, filename):
        print("done")
    def writing_curl_file_failed(self, collection, dataset_name, granules, err):
        print("raised", repr(err))

def main(data_center, project, update_collections, update_granules, events=Events(), temp_dir=TEMP_DIR, output_dir=OUTPUT_DIR):
    # Make sure temp_dir and output_dir exist
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Download all collections associated with `data_center` and `project` from CMR
    try:
        if not update_collections and is_cached("collections", temp_dir, data_center=data_center, project=project):
            try:
                events.collections_download_cached()
                collections = retrieve_cached("collections", temp_dir, data_center=data_center, project=project)['feed']['entry']
            except Exception as err: # If retrieving the cached collections failed, ...
                events.collections_download_cached_failed(err)
                events.collections_download_starting()
                collections = download_from_cmr("collections", temp_dir, data_center=data_center, project=project)['feed']['entry']
        else: # If using cached collections is disabled, ...
            events.collections_download_starting()
            collections = download_from_cmr("collections", temp_dir, data_center=data_center, project=project)['feed']['entry']
    except Exception as err:
        events.collections_download_failed(err)
        raise
    else:
        events.collections_download_succeeded(collections)

    for collection in collections:
        concept_id = collection['id']
        collection_shortname = collection['short_name']

        # Parse dataset name from short collection name
        dataset_name = collection_shortname[:collection_shortname.rfind('_')]

        # Download all granules associated with this concept ID from CMR
        try:
            if not update_granules and is_cached("granules", temp_dir, concept_id=concept_id):
                try:
                    events.granules_download_cached(collection, dataset_name)
                    granules = retrieve_cached("granules", temp_dir, concept_id=concept_id)['feed']['entry']
                except Exception as err: # If retrieving the cached granules failed, ...
                    events.granules_download_cached_failed(collection, dataset_name, err)
                    events.granules_download_starting(collection, dataset_name)
                    granules = download_from_cmr("granules", temp_dir, concept_id=concept_id)['feed']['entry']
            else: # If using cached granules is disabled, ...
                events.granules_download_starting(collection, dataset_name)
                granules = download_from_cmr("granules", temp_dir, concept_id=concept_id)['feed']['entry']
        except Exception as err:
            events.granules_download_failed(collection, dataset_name, err)
            raise
        else:
            events.granules_download_succeeded(collection, dataset_name, granules)

        # Create metadata directory for this dataset
        metadata_dir = os.path.join(output_dir, dataset_name, "metadata")
        if not os.path.exists(metadata_dir):
            os.makedirs(metadata_dir)

        # Create metadata cURL file
        events.writing_curl_file_starting(collection, dataset_name, granules)
        try:
            filename = os.path.join(metadata_dir, "metadata.curl")
            with open(filename, "w") as f:
                # Write cURL command to retrieve dataset metadata
                f.write(
                    "curl -s -o {}.json -H 'Accept: application/json' \"https://cmr.earthdata.nasa.gov/search/concepts/{}\"\n"
                    .format(dataset_name, concept_id)
                )

                for granule in granules:
                    granule_id = granule['id']
                    granule_title = granule['title']

                    # Parse granule name from granule title
                    granule_name = granule_title[len(dataset_name) + 1:granule_title.rfind('.')]

                    # Write cURL command to retrieve granule metadata
                    f.write(
                        "curl -s -o {}.json -H 'Accept: application/json' \"https://cmr.earthdata.nasa.gov/search/concepts/{}\"\n"
                        .format(granule_name, granule_id)
                    )
        except Exception as err:
            events.writing_curl_file_failed(collection, dataset_name, granules, err)
            raise
        else:
            events.writing_curl_file_succeeded(collection, dataset_name, granules, filename)

if __name__ == "__main__":
    # Parse command line arguments
    argparser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    argparser.add_argument(dest="data_center", help="data center to query for")
    argparser.add_argument(dest="project", help="project to query for")
    argparser.add_argument("--update-collections", dest="update_collections", help="ignore cached collections", action="store_true")
    argparser.add_argument("--update-granules", dest="update_granules", help="ignore cached granules", action="store_true")
    argparser.add_argument("--temp-dir", "-t", dest="temp_dir", default=TEMP_DIR, help="overwrite directory for CMR queries")
    argparser.add_argument("--output-dir", "-o", dest="output_dir", default=OUTPUT_DIR, help="overwrite directory for CMR queries")
    args = argparser.parse_args()

    print("")
    print("Creating metadata curl scripts with the following parameters:")
    for parameter, value in args.__dict__.items():
        print("  {}={}".format(parameter, value))
    print("")

    main(args.data_center, args.project, args.update_collections, args.update_granules, PrintEvents(), args.temp_dir, args.output_dir)
