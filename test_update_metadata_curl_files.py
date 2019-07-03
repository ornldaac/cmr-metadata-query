import functools
import json
import os
import os.path
import shutil
import stat
import tempfile
import unittest

import update_metadata_curl_files as umcf

CACHED_COLLECTIONS_1 = {
    "feed": {
        "entry": [
            {
                "id": "C1604360562-ORNL_DAAC",
                "short_name": "ABoVE_AirSWOT_Radar_Data_1646",
            }
        ]
    }
}
CACHED_COLLECTIONS_2 = {
    "feed": {
        "entry": [
            {
                "id": "C1604360562-ORNL_DAAC",
                "short_name": "ABoVE_AirSWOT_Radar_Data_1646",
            },
            {
                "id": "C1598211873-ORNL_DAAC",
                "short_name": "ABoVE_Airborne_AVIRIS_NG_1569",
            },
        ]
    }
}
CACHED_GRANULES_1 = {
    "feed": {
        "entry": [
            {
                "id": "G1604360612-ORNL_DAAC",
                "title": "ABoVE_AirSWOT_Radar_Data.elevation_utm_20170708171612.tif",
            }
        ]
    }
}

class TestException(Exception):
    pass

class TestEvents(umcf.PrintEvents):
    def __init__(self, unittest):
        self._unittest = unittest
        self._events = []
        self._broken = {}

        # Get all non-private, non-builtin methods of umcf.PrintEvents
        for event_name in dir(umcf.PrintEvents):
            event = getattr(self, event_name)
            if not event_name.startswith('_') and callable(event):
                # Override event with _event_called()
                setattr(self, event_name, functools.partial(self._event_called, event_name, event))

                # Create "broken" flag
                self._broken[event_name] = False

    def _event_called(self, event_name, event, *args, **kwargs):
        if self._broken[event_name]:
            self._broken[event_name] = False
            raise TestException

        self._events.append(event_name)
        event(*args, **kwargs)

    def assertEvents(self, *events):
        events = [ event.__name__ for event in events ]
        self._unittest.assertEqual(self._events, events)

    def set_broken(self, event):
        self._broken[event.__name__] = True

class TestMain(unittest.TestCase):
    def setUp(self):
        self.events = TestEvents(self)
        self.tmp_dir = tempfile.mkdtemp()
        self.bin_dir = tempfile.mkdtemp()
        self.PARAMS = {
            'data_center': "ORNL_DAAC",
            'project': "ABoVE",
            'update_collections': False,
            'update_granules': False,
            'events': self.events,
            'temp_dir': self.tmp_dir,
            'output_dir': self.bin_dir
        }
        return super(TestMain, self).setUp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        shutil.rmtree(self.bin_dir)
        return super(TestMain, self).tearDown()

    def test_broken_collections_download_uncached(self):
        self.events.set_broken(TestEvents.collections_download_starting)
        with self.assertRaises(TestException):
            umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_failed,
        )

    def test_collections_download_uncached(self):
        self.events.set_broken(TestEvents.granules_download_starting)
        self.events.set_broken(TestEvents.granules_download_failed)
        with self.assertRaises(TestException):
            umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_starting,
            TestEvents.collections_download_succeeded,
        )

    def test_collections_download_cached(self):
        # Create 1 cached collection
        with open(os.path.join(self.tmp_dir, "collections_ABoVE_ORNL_DAAC.json"), 'w') as file:
            json.dump(CACHED_COLLECTIONS_1, file)

        umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_cached,
            TestEvents.collections_download_succeeded,
            TestEvents.granules_download_starting,
            TestEvents.granules_download_succeeded,
            TestEvents.writing_curl_file_starting,
            TestEvents.writing_curl_file_succeeded,
        )

    def test_broken_granules_download(self):
        # Create 2 cached collections
        with open(os.path.join(self.tmp_dir, "collections_ABoVE_ORNL_DAAC.json"), 'w') as file:
            json.dump(CACHED_COLLECTIONS_2, file)

        self.events.set_broken(TestEvents.granules_download_starting)
        umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_cached,
            TestEvents.collections_download_succeeded,
            TestEvents.granules_download_failed,
            TestEvents.granules_download_starting,
            TestEvents.granules_download_succeeded,
            TestEvents.writing_curl_file_starting,
            TestEvents.writing_curl_file_succeeded,
        )

    def test_broken_collections_cached(self):
        # Create invalid cached collections
        with open(os.path.join(self.tmp_dir, "collections_ABoVE_ORNL_DAAC.json"), 'w') as file:
            file.write("INVALID JSON")

        self.events.set_broken(TestEvents.granules_download_starting)
        self.events.set_broken(TestEvents.granules_download_failed)
        with self.assertRaises(TestException):
            umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_cached,
            TestEvents.collections_download_cached_failed,
            TestEvents.collections_download_starting,
            TestEvents.collections_download_succeeded,
        )

    def test_broken_granules_cached(self):
        # Create 1 cached collection
        with open(os.path.join(self.tmp_dir, "collections_ABoVE_ORNL_DAAC.json"), 'w') as file:
            json.dump(CACHED_COLLECTIONS_1, file)

        # Create invalid cached granules
        with open(os.path.join(self.tmp_dir, "granules_C1604360562-ORNL_DAAC.json"), 'w') as file:
            file.write("INVALID JSON")

        umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_cached,
            TestEvents.collections_download_succeeded,
            TestEvents.granules_download_cached,
            TestEvents.granules_download_cached_failed,
            TestEvents.granules_download_starting,
            TestEvents.granules_download_succeeded,
            TestEvents.writing_curl_file_starting,
            TestEvents.writing_curl_file_succeeded,
        )

    def test_granules_cached(self):
        # Create 1 cached collection
        with open(os.path.join(self.tmp_dir, "collections_ABoVE_ORNL_DAAC.json"), 'w') as file:
            json.dump(CACHED_COLLECTIONS_1, file)

        # Create 1 cached granule
        with open(os.path.join(self.tmp_dir, "granules_C1604360562-ORNL_DAAC.json"), 'w') as file:
            json.dump(CACHED_GRANULES_1, file)

        umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_cached,
            TestEvents.collections_download_succeeded,
            TestEvents.granules_download_cached,
            TestEvents.granules_download_succeeded,
            TestEvents.writing_curl_file_starting,
            TestEvents.writing_curl_file_succeeded,
        )

    def test_curl_write_error(self):
        # Create 1 cached collection
        with open(os.path.join(self.tmp_dir, "collections_ABoVE_ORNL_DAAC.json"), 'w') as file:
            json.dump(CACHED_COLLECTIONS_1, file)

        # Create 1 cached granule
        with open(os.path.join(self.tmp_dir, "granules_C1604360562-ORNL_DAAC.json"), 'w') as file:
            json.dump(CACHED_GRANULES_1, file)

        # Create metadata directory for cached granule
        dataset_name = "ABoVE_AirSWOT_Radar_Data"
        metadata_dir = os.path.join(self.bin_dir, dataset_name, "metadata")
        os.makedirs(metadata_dir)

        # Create write protected metadata file to cause exception
        filename = os.path.join(metadata_dir, "metadata.curl")
        with open(filename, "w") as file:
            pass
        os.chmod(filename, stat.S_IREAD)

        umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_cached,
            TestEvents.collections_download_succeeded,
            TestEvents.granules_download_cached,
            TestEvents.granules_download_succeeded,
            TestEvents.writing_curl_file_starting,
            TestEvents.writing_curl_file_failed,
        )

        # Remove write protection on metadata file for cleanup
        os.chmod(filename, stat.S_IREAD or stat.S_IWRITE)

    def test_paging(self):
        # Create 1 cached collection
        with open(os.path.join(self.tmp_dir, "collections_ABoVE_ORNL_DAAC.json"), 'w') as file:
            json.dump(CACHED_COLLECTIONS_1, file)

        old_query_page_size = umcf.QUERY_PAGE_SIZE
        umcf.QUERY_PAGE_SIZE = 256
        try:
            umcf.main(**self.PARAMS)
            self.events.assertEvents(
                TestEvents.collections_download_cached,
                TestEvents.collections_download_succeeded,
                TestEvents.granules_download_starting,
                TestEvents.granules_download_succeeded,
                TestEvents.writing_curl_file_starting,
                TestEvents.writing_curl_file_succeeded,
            )
        finally:
            umcf.QUERY_PAGE_SIZE = old_query_page_size

    def test_inexistant_folders(self):
        tmp_dir = os.path.join(self.tmp_dir, "tmp_dir")
        bin_dir = os.path.join(self.bin_dir, "bin_dir")

        self.PARAMS['temp_dir'] = tmp_dir
        self.PARAMS['output_dir'] = bin_dir

        self.assertFalse(os.path.exists(tmp_dir))
        self.assertFalse(os.path.exists(bin_dir))

        self.events.set_broken(TestEvents.collections_download_starting)
        with self.assertRaises(TestException):
            umcf.main(**self.PARAMS)
        self.events.assertEvents(
            TestEvents.collections_download_failed,
        )

        self.assertTrue(os.path.exists(tmp_dir))
        self.assertTrue(os.path.exists(bin_dir))

if __name__ == "__main__":
    unittest.main()