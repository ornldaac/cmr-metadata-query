import json
import os.path
import requests

TEMP_DIR = "./tmp" # The directory, used to store all data retrieved from the CMR search API in JSON files
OUTPUT_DIR = "./out" # The directory, used to store all generated metadata in cURL files
QUERY_PAGE_SIZE = 2000 # The page size for CMR search results

def download_from_cmr(what, **params):
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
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.loads(f.read())

    # Issue query to the CMR search API
    params["page_size"] = QUERY_PAGE_SIZE
    for page_num in range(1, 1000000 // QUERY_PAGE_SIZE):
        # Set page number parameter
        if page_num != 1:
            params["page_num"] = page_num

        # Query one page of search results
        request = requests.get(
            "https://cmr.earthdata.nasa.gov/search/" + what,
            params=params,
            headers={ "Accept": "application/json" }
        )
        json_response_page = request.json()
        page_entries = json_response_page['feed']['entry']

        if page_num == 1: # If this is the first page
            json_response = json_response_page # Set json_response
        else:  # If this isn't the first page
            json_response['feed']['entry'] += page_entries # Append entries of this page to json_response
        
        # Stop requesting new pages as soon as no more entries are returned
        if not page_entries:
            break

    # Save results to JSON file
    with open(filename, "w") as f:
        f.write(json.dumps(json_response, indent=4))

    return json_response


if __name__ == "__main__":
    # Make sure TEMP_DIR and OUTPUT_DIR exist
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Download all collections of the ORNL-DAAC ABoVE project from CMR
    print("retrieving collections ...")
    collections = download_from_cmr("collections", data_center="ORNL_DAAC", project="ABoVE")['feed']['entry']
    print("got {} collections".format(len(collections)))

    for collection in collections:
        concept_id = collection['id']
        collection_shortname = collection['short_name']

        # Parse dataset name from short collection name
        dataset_name = collection_shortname[:collection_shortname.rfind('_')]

        # Download all granules associated with this concept ID from CMR
        print("retrieving granules for dataset '{}' ...".format(dataset_name))
        granules = download_from_cmr("granules", concept_id=concept_id)['feed']['entry']
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

