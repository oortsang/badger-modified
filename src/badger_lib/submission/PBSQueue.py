__author__ = "alvaro barbeira"

import copy
import os
import logging
import time

from subprocess import Popen, PIPE

from .. import Configuration, Item

K_JOBS_FOLDER="jobs_folder"
K_JOB_NAME_KEY="job_name_key"
K_SUBMISSION="__submission"
K_SUBMISSION_STATUS="submission_status"
K_JOB_ID="job_id"
K_FAKE_SUBMISSION="fake_submission"
K_Crude_SUBMISSION="crude_submission"

class PBSQueueSubmission:
    def __init__(self, jobs_folder, job_name_key, fake_submission, crude_submission):
        self.jobs_folder = jobs_folder
        self.job_name_key = job_name_key
        self.fake_submission = fake_submission
        self.crude_submission = crude_submission
        self._counter = 0

    def __deepcopy__(self, memodict={}):
        return PBSQueueSubmission(self.jobs_folder, self.job_name_key, self.fake_submission, self.crude_submission)

    def submit(self, item, render, configuration):
        if self.jobs_folder:
            if not os.path.exists(self.jobs_folder): os.makedirs(self.jobs_folder)

        item = copy.deepcopy(item)

        job_path = self._job_path(item)
        if os.path.exists(job_path):
            logging.info("%s already exists, skipping", job_path)
            Item._add_key_value_to_metadata(item, _sp(K_SUBMISSION_STATUS), "skipped")
            return item

        with open(job_path, "w") as f:
            f.write(render)

        job_id = _submit(job_path, self.fake_submission, self.crude_submission)

        Item._add_key_value_to_metadata(item, _sp("job_path"), job_path)
        status = "submitted" if job_id else "submission_failed"
        Item._add_key_value_to_metadata(item, _sp(K_SUBMISSION_STATUS), status)
        Item._add_key_value_to_metadata(item, _sp(K_JOB_ID), job_id)

        return item

    def to_dict(self):
        return {K_JOBS_FOLDER: self.jobs_folder, K_JOB_NAME_KEY:self.job_name_key, K_FAKE_SUBMISSION:self.fake_submission, K_Crude_SUBMISSION:self.crude_submission}

    @classmethod
    def from_dict(cls, d):
        return PBSQueueSubmission(d.get(K_JOBS_FOLDER), d.get(K_JOB_NAME_KEY), d.get(K_FAKE_SUBMISSION), d.get(K_Crude_SUBMISSION))

    def _job_path(self, item):
        if self.job_name_key:
            p = "{}.sh".format(Item._get_argument_value(item, self.job_name_key))
        else:
            p = "{}.sh".format(self._counter)
            self._counter += 1

        if self.jobs_folder:
            p = os.path.join(self.jobs_folder, p)

        return p

    def explain(self, item):
        status =Item._get_metadata(item, _sp(K_SUBMISSION_STATUS))
        if self.job_name_key:
            name = Item._get_argument_value(item, self.job_name_key) if self.job_name_key in item[Configuration.K_ARGUMENTS] else "anonimous"
        job_id =  Item._get_metadata(item, _sp(K_JOB_ID))
        return "{}:{}:{}".format(name, status, job_id)

def _sp(path): return os.path.join(K_SUBMISSION, path)

def _submit(path, fake=False, crude=False):
    if fake:
        return path
    if crude:
        command = ["bash",path]
    else:
        command = ["qsub",path]
    def submit():
        logging.log(7,"Submitting Command: %s", " ".join(command))
        proc = Popen(command,stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        exitcode = proc.returncode
        return exitcode, out, err

    exitcode, out, err = submit()
    retry=0
    while exitcode != 0 and retry < 10:
        logging.info("retry, %i-th attempt: %s", retry, path)
        exitcode, out, err = submit()
        retry += 1
        time.sleep(0.1)
    time.sleep(0.1)
    job_id = out.strip().decode() if exitcode==0 else None
    return job_id