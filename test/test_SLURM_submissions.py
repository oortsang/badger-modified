import unittest
import os

from src.badger import badger
from src.badger_lib import Batches

K_TEST_WORKSPACE = "temp"

class FakeSubmissionTestCase(unittest.TestCase):
    def setUp(self):
        assert not os.path.isdir(K_TEST_WORKSPACE), "Trying to work in {}!".format(K_TEST_WORKSPACE)
        os.mkdir(K_TEST_WORKSPACE)

    def tearDown(self):
        os.rmdir(K_TEST_WORKSPACE)

    def test_fake_submission_1(self):
