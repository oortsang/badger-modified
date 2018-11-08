__author__ = "alvaro barbeira"
import os
import re
import logging
import copy

from . import Arguments
from .. import Item

K_START="start"
K_END="end"
K_VALUES="values"
K_FILE_LIST="file_list"

class Range(Arguments.Argument):
    def __init__(self, start, end, values, file_list,  name=None, prefix=None, metadata_rules=None):
        super().__init__(name, prefix, metadata_rules)
        self.start = start
        self.end = end
        self.values = values
        self.file_list = file_list

    def __deepcopy__(self, memodict={}):
        return Range(self.start, self.end, self.values, self.file_list, self.name, self.prefix, self.metadata_rules)

    def _loop(self, command_set):
        logging.log(6, "Looping Range:{}".format(self.name))
        for item in Arguments._generate(command_set):
            if self.values:
                range_ = self.values
            elif self.file_list:
                range_ = Arguments._load(self.file_list)
            elif self.start is not None and self.end is not None:
                range_ = range(self.start, self.end)
            else:
                raise RuntimeError("In valid range arguments")

            for i in range_:
                item_ = Item._copy(item)
                yield item_, str(i)

    def _apply(self, item, i):
        return Item._apply_argument_to_item(item, self.name, self.prefix, i)

    def to_dict(self):
        d = super().to_dict()
        d[K_START] = self.start
        d[K_END] = self.end
        d[K_VALUES] = self.values
        d[K_FILE_LIST] = self.file_list
        return d

    @classmethod
    def from_dict(cls, d):
        return Range(d.get(K_START),
                    d.get(K_END),
                    d.get(K_VALUES),
                    d.get(K_FILE_LIST),
                    name=d.get(Arguments.K_NAME),
                    prefix=d.get(Arguments.K_PREFIX),
                    metadata_rules=d.get(Arguments.K_METADATA_RULES))
