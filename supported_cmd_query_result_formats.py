"""
Supported response formats for the following CMR queries:

* https://cmr.earthdata.nasa.gov/search/collections
* https://cmr.earthdata.nasa.gov/search/granules
* https://cmr.earthdata.nasa.gov/search/concepts

*Note: This file is only used for documentation. It is not imported by update_metadata_curl_files.py.*
"""

class QueryResultFormat(object):
    def __init__(self, accept_header, file_ext):
        self.accept_header = accept_header
        self.file_ext = file_ext

SUPPORTED_COLLECTION_FORMATS = {
    "json": QueryResultFormat("application/json", "json"),
    "xml": QueryResultFormat("application/xml", "xml"),
    "echo10": QueryResultFormat("application/echo10+xml", "xml"),
    "iso": QueryResultFormat("application/iso19115+xml", "xml"),
    "iso19115": QueryResultFormat("application/iso19115+xml", "xml"),
    "atom": QueryResultFormat("application/atom+xml", "xml"),
    "kml": QueryResultFormat("application/vnd.google-earth.kml+xml", "xml"),
    "native": QueryResultFormat("application/metadata+xml", "xml"),
    "umm_json": QueryResultFormat("application/vnd.nasa.cmr.umm+json", "json"),
    "umm_json_v1_0": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.0", "json"),
    "umm_json_v1_1": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.1", "json"),
    "umm_json_v1_2": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.2", "json"),
    "umm_json_v1_3": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.3", "json"),
    "umm_json_v1_4": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.4", "json"),
    "umm_json_v1_5": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.5", "json"),
    "umm_json_v1_6": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.6", "json"),
    "umm_json_v1_7": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.7", "json"),
    "umm_json_v1_8": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.8", "json"),
    "umm_json_v1_9": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.9", "json"),
    "umm_json_v1_10": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.10", "json"),
    "umm_json_v1_11": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.11", "json"),
    "umm_json_v1_12": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.12", "json"),
    "umm_json_v1_13": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.13", "json"),
    "dif": QueryResultFormat("application/dif+xml", "xml"),
    "dif10": QueryResultFormat("application/dif10+xml", "xml"),
    "opendata": QueryResultFormat("application/opendata+json", "json"),
}
DEFAULT_COLLECTION_FORMAT = "json"
SUPPORTED_GRANULE_FORMATS = {
    "json": QueryResultFormat("application/json", "json"),
    "xml": QueryResultFormat("application/xml", "xml"),
    "echo10": QueryResultFormat("application/echo10+xml", "xml"),
    "iso": QueryResultFormat("application/iso19115+xml", "xml"),
    "iso19115": QueryResultFormat("application/iso19115+xml", "xml"),
    "csv": QueryResultFormat("text/csv", "csv"),
    "atom": QueryResultFormat("application/atom+xml", "xml"),
    "kml": QueryResultFormat("application/vnd.google-earth.kml+xml", "xml"),
    "native": QueryResultFormat("application/metadata+xml", "xml"),
    "umm_json": QueryResultFormat("application/vnd.nasa.cmr.umm+json", "json"),
    "umm_json_v1_0": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.0", "json"),
    "umm_json_v1_1": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.1", "json"),
    "umm_json_v1_2": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.2", "json"),
    "umm_json_v1_3": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.3", "json"),
    "umm_json_v1_4": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.4", "json"),
    "umm_json_v1_5": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.5", "json"),
    "umm_json_v1_6": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.6", "json"),
    "umm_json_v1_7": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.7", "json"),
    "umm_json_v1_8": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.8", "json"),
    "umm_json_v1_9": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.9", "json"),
    "umm_json_v1_10": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.10", "json"),
    "umm_json_v1_11": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.11", "json"),
    "umm_json_v1_12": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.12", "json"),
    "umm_json_v1_13": QueryResultFormat("application/vnd.nasa.cmr.umm_results+json; version=1.13", "json"),
}
DEFAULT_GRANULE_FORMAT = "json"
SUPPORTED_CONCEPT_FORMATS = {
    "json": QueryResultFormat("application/json", "json"),
    "xml": QueryResultFormat("application/xml", "xml"),
    "echo10": QueryResultFormat("application/echo10+xml", "xml"),
    "iso": QueryResultFormat("application/iso19115+xml", "xml"),
    "iso19115": QueryResultFormat("application/iso19115+xml", "xml"),
    "atom": QueryResultFormat("application/atom+xml", "xml"),
    "native": QueryResultFormat("application/metadata+xml", "xml"),
    "umm_json": QueryResultFormat("application/vnd.nasa.cmr.umm+json", "json"),
    "dif": QueryResultFormat("application/dif+xml", "xml"),
    "dif10": QueryResultFormat("application/dif10+xml", "xml"),
}
DEFAULT_CONCEPT_FORMAT = "json"