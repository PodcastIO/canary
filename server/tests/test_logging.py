import unittest

import podcast.pkg.client.log as logging


class LoggingTest(unittest.TestCase):
    def test_logging(self):
        logging.warning("abc, %s", 123)
