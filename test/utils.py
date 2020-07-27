import os
from shutil import rmtree

from . import config
from src.badger_lib.yaml_support import YAML
from src.badger_lib import Configuration

def _setUp():
    assert not os.path.isdir(config.K_TEST_WORKSPACE), "Trying to work in {}!".format(config.K_TEST_WORKSPACE)
    os.mkdir(config.K_TEST_WORKSPACE)


def _tearDown():
    rmtree(config.K_TEST_WORKSPACE)


def load_YAML_append_test_workspace(fp):
    """
    Created to load yaml configuration files and ensure that all jobs are
    targeted to the test workspace directory.
    returns: (Configuration object, jobs target path)
    """
    YAML.initialize_yaml()
    configuration = YAML.load_yaml(fp)
    initial_config_joblib = configuration[Configuration.K_DEFINITIONS][Configuration.K_SUBMISSION].jobs_folder
    new_config_joblib = os.path.join(config.K_TEST_WORKSPACE, initial_config_joblib)
    configuration[Configuration.K_DEFINITIONS][Configuration.K_SUBMISSION].jobs_folder = new_config_joblib

    return (configuration, new_config_joblib)
