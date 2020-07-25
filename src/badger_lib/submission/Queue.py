__author__ = "alvaro barbeira"

import copy
import os
import logging
import time

from .. import Configuration, Item

K_JOBS_FOLDER="jobs_folder"
K_JOB_NAME_KEY="job_name_key"
K_SUBMISSION="__submission"
K_SUBMISSION_STATUS="submission_status"
K_JOB_ID="job_id"
K_FAKE_SUBMISSION="fake_submission"
K_Crude_SUBMISSION="crude_submission"
K_SUBMIT_FUNCTION="submit_function"


class QueueSubmission:
    def __init__(self, jobs_folder, job_name_key, fake_submission,
                 submit_f):
        self.jobs_folder = jobs_folder
        self.job_name_key = job_name_key
        self.fake_submission = fake_submission
        self.submit_f = submit_f
        self._counter = 0

    def __deepcopy__(self, memodict={}):
        return QueueSubmission(self.jobs_folder, self.job_name_key,
                               self.fake_submission, self.submit_f)

    def submit(self, item, render, configuration):
        if self.jobs_folder:
            if not os.path.exists(self.jobs_folder):
                os.makedirs(self.jobs_folder)

        item = copy.deepcopy(item)

        job_path = self._job_path(item)
        if os.path.exists(job_path):
            logging.info("%s already exists, skipping", job_path)
            Item._add_key_value_to_metadata(item, self._sp(K_SUBMISSION_STATUS), "skipped")
            return item

        with open(job_path, "w") as f:
            f.write(render)

        if self.fake_submission:
            job_id = job_path
            status = 'fake_submit'
        else:
            job_id = self.submit_f(job_path)
            status = "submitted" if job_id else "submission_failed"

        Item._add_key_value_to_metadata(item, self._sp("job_path"), job_path)
        Item._add_key_value_to_metadata(item, self._sp(K_SUBMISSION_STATUS),
                                        status)
        Item._add_key_value_to_metadata(item, self._sp(K_JOB_ID), job_id)

        return item

    def to_dict(self):
        return {K_JOBS_FOLDER: self.jobs_folder,
                K_JOB_NAME_KEY: self.job_name_key,
                K_FAKE_SUBMISSION: self.fake_submission,
                K_SUBMIT_FUNCTION: self.submit_f}

    @classmethod
    def from_dict(cls, d):
        return QueueSubmission(d.get(K_JOBS_FOLDER),
                               d.get(K_JOB_NAME_KEY),
                               d.get(K_FAKE_SUBMISSION),
                               d.get(K_SUBMIT_FUNCTION))

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
        name = "anonimous"
        if self.job_name_key and \
                (self.job_name_key in item[Configuration.K_ARGUMENTS]):
                name = Item._get_argument_value(item, self.job_name_key)
        job_id =  Item._get_metadata(item, self._sp(K_JOB_ID))
        return "{}:{}:{}".format(name, status, job_id)

    @staticmethod
    def _sp(path):
        return os.path.join(K_SUBMISSION, path)

