import os
from shutil import which
K_TEST_WORKSPACE = "temp"

def _setUp():
    assert not os.path.isdir(K_TEST_WORKSPACE), "Trying to work in {}!".format(K_TEST_WORKSPACE)
    os.mkdir(K_TEST_WORKSPACE)


def _tearDown():
    os.rmdir(K_TEST_WORKSPACE)

def _is_sbatch_available():
    return which("sbatch") is not None
