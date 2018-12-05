"""
Utility for creating metadata curl scripts by querying https://cmr.earthdata.nasa.gov.

This script does the following:
1) Download a list of all ORNL DAAC collections from CMR.
2) Download a list of all granules for each collection from CMR.
3) Create a metadata.curl file in the output directory for each collection.
   A metadata.curl file contains curl commands to download each granule of the collection.

The raw output of each CMR query in steps 1 & 2 is stored in the temporary directory.
This behaviour can be disabled with command line flags to check for changes on the CMR.

Written 10/2018 by S. Klaassen
"""


from argparse import ArgumentParser, RawTextHelpFormatter
import json
import math
import os.path
import requests

TEMP_DIR = "./tmp" # The directory, used to store all data retrieved from the CMR search API in JSON files
OUTPUT_DIR = "./out" # The directory, used to store all generated metadata in cURL files
QUERY_PAGE_SIZE = 2000 # The page size for CMR search results

def download_from_cmr(what, ignore_cache=False, **params):
    """Issue a search query to CMR and return a dict of the JSON response

    For documentation on what can be searched for on the CMR, refer to
    https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#collection-search-by-parameters
    (Parameters to this function correspond the chapter: "Find `what` by `params`").

    Results are stored in a JSON file in the `TEMP_DIR` directory.
    Subsequent searches will return stored results, if available.
    
    Args:
        what (String): The type of data to find
        params (String): Search criteria and parameter options
    
    Returns:
        dict: JSON response content
    """

    filename = os.path.join(TEMP_DIR, "{}_{}.json".format(what, '_'.join(params.values())))

    # Return previousely downloaded results from JSON file, if available
    if not ignore_cache and os.path.exists(filename):
        with open(filename, "r") as f:
            return json.loads(f.read())

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


if __name__ == "__main__":
    # Parse command line arguments
    argparser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    argparser.add_argument("--update-collections", dest="update_collections", help="ignore cached collections", action="store_true")
    argparser.add_argument("--update-granules", dest="update_granules", help="ignore cached granules", action="store_true")
    args = argparser.parse_args()

    # Make sure TEMP_DIR and OUTPUT_DIR exist
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Download all collections of the ORNL-DAAC ABoVE project from CMR
    print("retrieving collections ...")
    collections = download_from_cmr("collections", ignore_cache=args.update_collections, data_center="ORNL_DAAC", project="ABoVE")['feed']['entry']
    print("got {} collections".format(len(collections)))

    for collection in collections:
        concept_id = collection['id']
        collection_shortname = collection['short_name']

        # Parse dataset name from short collection name
        dataset_name = collection_shortname[:collection_shortname.rfind('_')]

        # Download all granules associated with this concept ID from CMR
        print("retrieving granules for dataset '{}' ...".format(dataset_name))
        granules = download_from_cmr("granules", ignore_cache=args.update_granules, concept_id=concept_id)['feed']['entry']
        print("got {} granules".format(len(granules)))

        # Create metadata directory for this dataset
        metadata_dir = os.path.join(OUTPUT_DIR, dataset_name, "metadata")
        if not os.path.exists(metadata_dir):
            os.makedirs(metadata_dir)

        # Create metadata cURL file
        print("writing curl commands ...")
        with open(os.path.join(metadata_dir, "metadata.curl"), "w") as f:
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
        print("done")

    print("finished")

