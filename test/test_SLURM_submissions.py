import unittest
import os
from shutil import which

from src.badger_lib import Batches
from src.badger_lib.yaml_support import YAML
from . import utils
from . import config



class FakeSubmissionTest(unittest.TestCase):

    def setUp(self):
        utils._setUp()

    def tearDown(self):
        utils._tearDown()

    def test_1(self):
        yaml_fp = 'test/resources/configurations/range_SLURM_submission.yaml'
        configuration, jobs_target = utils.load_YAML_append_test_workspace(yaml_fp)
        Batches._process(configuration)
        jobs_lst = os.listdir(jobs_target)
        self.assertEqual(len(jobs_lst), 22)


class RealSubmissionTest(unittest.TestCase):
    def setUp(self):
        utils._setUp()

    def tearDown(self):
        utils._tearDown()

    @unittest.skipUnless(config.BOOL_RUN_SBATCH, "sbatch not available")
    def test_real_submission_1(self):
        yaml_fp = 'test/resources/configurations/range_SLURM_submission.yaml'
        YAML.initialize_yaml()
        config = YAML.load_yaml(yaml_fp)
        pass
