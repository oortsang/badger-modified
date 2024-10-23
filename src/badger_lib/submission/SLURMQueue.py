__author__ = "alvaro barbeira"

import logging
import time

from subprocess import Popen, PIPE

from . import Queue

K_JOBS_FOLDER = "jobs_folder"
K_JOB_NAME_KEY = "job_name_key"
K_SUBMISSION = "__submission"
K_SUBMISSION_STATUS = "submission_status"
K_JOB_ID = "job_id"
K_FAKE_SUBMISSION = "fake_submission"
K_Crude_SUBMISSION = "crude_submission"
K_SUBMIT_FUNCTION = "submit_function"
CONST_SLEEP_TIME = 1.0
K_OVERWRITE_SCRIPTS = "overwrite_scripts"


class SLURMQueueSubmission(Queue.QueueSubmission):
    def __init__(self, jobs_folder, job_name_key, fake_submission, overwrite_scripts=False):
        super(SLURMQueueSubmission, self).__init__(
            jobs_folder, job_name_key, fake_submission, SLURM_submit,
            overwrite_scripts=overwrite_scripts,
        )

    def __deepcopy__(self, memodict={}):
        return SLURMQueueSubmission(
            self.jobs_folder, self.job_name_key, self.fake_submission
        )

    def to_dict(self):
        return {
            K_JOBS_FOLDER: self.jobs_folder,
            K_JOB_NAME_KEY: self.job_name_key,
            K_FAKE_SUBMISSION: self.fake_submission,
            K_OVERWRITE_SCRIPTS: self.overwrite_scripts,
        }

    @classmethod
    def from_dict(cls, d):
        return SLURMQueueSubmission(
            d.get(K_JOBS_FOLDER), d.get(K_JOB_NAME_KEY), d.get(K_FAKE_SUBMISSION),
            d.get(K_OVERWRITE_SCRIPTS, False), # by default, don't overwrite
        )


def SLURM_submit(path):
    command = ["sbatch", path]

    def submit():
        logging.log(7, "Submitting Command: %s", " ".join(command))
        proc = Popen(command, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode
        return exitcode, out, err

    exitcode, out, err = submit()
    retry = 0
    while exitcode != 0 and retry < 10:
        logging.info("retry, %i-th attempt: %s", retry, path)
        exitcode, out, err = submit()
        retry += 1
        time.sleep(CONST_SLEEP_TIME)
    time.sleep(CONST_SLEEP_TIME)
    job_id = out.strip().decode() if exitcode == 0 else None
    return job_id
