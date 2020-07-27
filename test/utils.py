import os
from shutil import rmtree
import unittest

from . import config
from src.badger_lib.yaml_support import YAML
from src.badger_lib import Configuration

def _setUp():
    assert not os.path.isdir(config.K_TEST_WORKSPACE), "Trying to work in {}!".format(config.K_TEST_WORKSPACE)
    os.mkdir(config.K_TEST_WORKSPACE)


def _tearDown():
    rmtree(config.K_TEST_WORKSPACE)


def load_YAML_append_test_workspace(fp, to_real_submission=False, assert_type=None):
    """

    :param fp: filepath to yaml
    :param to_real_submission: whether to amend configuration to disable fake submission
    :return: (Configuration object, jobs target path)
    """
    YAML.initialize_yaml()
    configuration = YAML.load_yaml(fp)
    initial_config_joblib = configuration[Configuration.K_DEFINITIONS][Configuration.K_SUBMISSION].jobs_folder
    new_config_joblib = os.path.join(config.K_TEST_WORKSPACE, initial_config_joblib)
    configuration[Configuration.K_DEFINITIONS][Configuration.K_SUBMISSION].jobs_folder = new_config_joblib

    if to_real_submission:
        configuration[Configuration.K_DEFINITIONS][Configuration.K_SUBMISSION].fake_submission = False

    if assert_type is not None:
        assert type(configuration[Configuration.K_DEFINITIONS][Configuration.K_SUBMISSION]) == assert_type

    return (configuration, new_config_joblib)