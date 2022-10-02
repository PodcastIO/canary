import unittest

from rq import Worker

from podcast.pkg.client.redis import redis_connection


class TestTextPDF(unittest.TestCase):
    def test_parse_pdf(self):
        # Returns all workers registered in this connection
        workers = Worker.all(connection=redis_connection)
        print(workers)