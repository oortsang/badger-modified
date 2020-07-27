import unittest
import os
from shutil import which

from src.badger_lib import Batches
from src.badger_lib.yaml_support import YAML
from . import utils



class FakeSubmissionTest(unittest.TestCase):

    def setUp(self):
        utils._setUp()

    def tearDown(self):
        utils._tearDown()

    def test_1(self):
        yaml_fp = 'test/resources/configurations/range_SLURM_submission.yaml'
        Batches.process(yaml_fp)
        jobs_folder = "temp/jobs"
        jobs_lst = os.listdir(jobs_folder)
        self.assertEqual(len(jobs_lst), 22)


class RealSubmissionTest(unittest.TestCase):
    def setUp(self):
        utils._setUp()

    def tearDown(self):
        utils._tearDown()

    @unittest.skipUnless(utils._is_sbatch_available(), "sbatch not available")
    def test_real_submission_1(self):
        yaml_fp = 'test/resources/configurations/range_SLURM_submission.yaml'
        YAML.initialize_yaml()
        config = YAML.load_yaml(yaml_fp)
        pass
