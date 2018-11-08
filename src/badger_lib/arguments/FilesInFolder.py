__author__ = "alvaro barbeira"
import os
import re
import logging
import copy

from . import Arguments
from .. import Item

K_FOLDER="folder"
K_REGEXP_FILTER="regexp_filter"
K_SORT="sort"

class FilesInFolder(Arguments.Argument):
    def __init__(self, folder, regexp_filter, sort, name=None, prefix=None, metadata_rules=None):
        super().__init__(name, prefix, metadata_rules)
        self.sort = sort
        self.folder = folder
        self.regexp = re.compile(regexp_filter) if regexp_filter else None

    def __deepcopy__(self, memodict={}):
        return FilesInFolder(self.folder, self.regexp.pattern, self.sort, self.name, self.prefix, self.metadata_rules)

    def _loop(self, command_set):
        logging.log(6, "Looping FilesInFolder:{}".format(self.name))
        contents = os.listdir(self.folder)
        if self.regexp:
            contents = [x for x in contents if self.regexp.search(x)]
        if self.sort:
            contents = sorted(contents)
        contents = [os.path.join(self.folder,x) for x in contents]

        for item in Arguments._generate(command_set):
            for c in contents:
                item_ = Item._copy(item)
                yield item_, c

    def _apply(self, item, path):
        return Item._apply_argument_to_item(item, self.name, self.prefix, path)

    def to_dict(self):
        d = super().to_dict()
        d[K_FOLDER] = self.folder
        d[K_REGEXP_FILTER] = self.regexp.pattern
        d[K_SORT] = self.sort
        return d

    @classmethod
    def from_dict(cls, d):
        return FilesInFolder(d.get(K_FOLDER),
                             d.get(K_REGEXP_FILTER),
                             d.get(K_SORT),
                             name=d.get(Arguments.K_NAME),
                             prefix=d.get(Arguments.K_PREFIX),
                             metadata_rules=d.get(Arguments.K_METADATA_RULES))


class ExtractFromFileNameRegexpMetadata(Arguments.ExtractFromValueWithRegexpMetadata):
    def __init__(self, strict, name=None, path=None):
        super().__init__(None, strict, name, path)

    def __deepcopy__(self, memodict={}):
        return ExtractFromFileNameRegexpMetadata(self.strict, self.name, self.path)

    def __call__(self, item, argument, value, *args, **kwargs):
        if not isinstance(argument, FilesInFolder):
            raise RuntimeError("This rule expects a FilesInFolder argument")
        if not self.regexp:
            if not argument.regexp:
                raise RuntimeError("No regexp found for extraction from FilesInFolder")
            self.regexp = argument.regexp
        logging.log(5, "Extracting from {}".format(value))
        v = os.path.split(value)[1]
        super().__call__(item, argument, v, args, kwargs)

    @classmethod
    def from_dict(cls, d):
        return ExtractFromFileNameRegexpMetadata(d.get(Arguments.K_STRICT), name=d.get(Arguments.K_NAME), path=d.get(Arguments.K_PATH))