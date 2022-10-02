import unittest

from pkg.gid.global_id import GlobalId


class GlobalIdTest(unittest.TestCase):
    def test_gid(self):
        gid1 = GlobalId()
        gid2 = GlobalId()
        self.assertNotEqual(gid1, gid2)
