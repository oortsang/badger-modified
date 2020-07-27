import unittest
import os
from shutil import which

from src.badger_lib import Batches
from src.badger_lib.yaml_support import YAML
from src.badger_lib.submission.PBSQueue import PBSQueueSubmission
from . import utils
from . import config



class FakeSubmissionTest(unittest.TestCase):

    def setUp(self):
        utils._setUp()

    def tearDown(self):
        utils._tearDown()

    def test_1(self):
        yaml_fp = 'test/resources/configurations/range_PBS_submission.yaml'
        configuration, jobs_target = utils.load_YAML_append_test_workspace(yaml_fp,
                                                                           assert_type=PBSQueueSubmission)
        Batches._process(configuration)
        jobs_lst = os.listdir(jobs_target)
        self.assertEqual(len(jobs_lst), 22)

    def test_2(self):
        yaml_fp = 'test/resources/configurations/filesinfolder_PBS_submission.yaml'
        configuration, jobs_target = utils.load_YAML_append_test_workspace(yaml_fp,
                                                                           assert_type=PBSQueueSubmission)
        Batches._process(configuration)
        jobs_lst = os.listdir(jobs_target)
        self.assertEqual(len(jobs_lst), 10)


class RealSubmissionTest(unittest.TestCase):
    def setUp(self):
        utils._setUp()

    def tearDown(self):
        utils._tearDown()

    @unittest.skipUnless(config.BOOL_RUN_SBATCH, "sbatch not available")
    def test_real_submission_1(self):
        yaml_fp = 'test/resources/configurations/range_PBS_submission.yaml'
        configuration, jobs_target = utils.load_YAML_append_test_workspace(yaml_fp,
                                                                           assert_type=PBSQueueSubmission,
                                                                           to_real_submission=True)
        Batches._process(configuration)
        jobs_lst = os.listdir(jobs_target)
        self.assertEqual(len(jobs_lst), 22)

    @unittest.skipUnless(config.BOOL_RUN_SBATCH, "sbatch not available")
    def test_2(self):
        yaml_fp = 'test/resources/configurations/filesinfolder_PBS_submission.yaml'
        configuration, jobs_target = utils.load_YAML_append_test_workspace(yaml_fp,
                                                                           assert_type=PBSQueueSubmission,
                                                                           to_real_submission=True)
        Batches._process(configuration)
        jobs_lst = os.listdir(jobs_target)
        self.assertEqual(len(jobs_lst), 10)