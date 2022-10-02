import unittest

from internal.resource.resource import Resource as InternalResource


class BookTest(unittest.TestCase):
    def test_resource(self):
        with InternalResource(gid="616d9000f8cd79ad59ee8f34") as resource:
            resource
