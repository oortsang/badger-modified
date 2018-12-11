from badger_lib.arguments.Arguments import _load

__author__ = "alvaro barbeira"

import logging
import os
from . import Arguments
from .. import Item

K_LIST="using_list"
K_LIST_FROM_FILE="list_from_file"
K_IN_METADATA_PATH="in_metadata_path"

class Blacklist(Arguments.Argument):
    def __init__(self, from_list, list_from_file, in_metadata_path, name=None, prefix=None, metadata_rules=None):
        super().__init__(name, prefix, metadata_rules)
        #Watchout: it seems that parsing is two-step so that we get incomplete types, can't check complete arguments
        #if from_list:
        #    raise RuntimeError("Using list is broken. Use list_from_file.")
        #if not from_list and not list_from_file:
        #    raise RuntimeError("Provide either -list- or -list_from_file- argument for Blacklist")
        if not in_metadata_path:
            raise RuntimeError("For the moment, in_metadata_path is required")
        self.list = from_list
        self.list_from_file = list_from_file
        self.in_metadata_path = in_metadata_path

    def __deepcopy__(self, memodict={}):
        return Blacklist(self.list, self.list_from_file, self.in_metadata_path, self.name, self.prefix, self.metadata_rules)

    def _loop(self, command_set):
        logging.log(6, "Looping Blacklist:{}/{}".format(self.list, self.list_from_file))
        l = self.list if self.list else _load(_get_path(self))
        l = {x for x in l}
        for item in Arguments._generate(command_set):
            m = Item._get_metadata(item, self.in_metadata_path)
            if m in l:
                logging.log(6, "%s in Blacklist", m)
                continue
            else:
                logging.log(6, "%s not in Blacklist", m)
            yield item, None

    def _apply(self, item, value):
        return item

    def to_dict(self):
        d = super().to_dict()
        d[K_LIST] = self.list
        d[K_LIST_FROM_FILE] = self.list_from_file
        d[K_IN_METADATA_PATH] = self.in_metadata_path
        return d

    @classmethod
    def from_dict(cls, d):
        return Blacklist(d.get(K_LIST),
                    d.get(K_LIST_FROM_FILE),
                    d.get(K_IN_METADATA_PATH),
                    name = d.get(Arguments.K_NAME),
                    prefix = d.get(Arguments.K_PREFIX),
                    metadata_rules = d.get(Arguments.K_METADATA_RULES))

#this has to go too
def _get_path(item):
    path = item.list_from_file
    if os.path.isabs(path):
        return path
    raise RuntimeError("This is broken. Use absolute path.")
    return os.path.join(Item._get_metadata(item, Item.K_CONFIGURATION_BASE_PATH), path)