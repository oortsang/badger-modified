__author__ = "alvaro barbeira"

import logging
import os
from . import Arguments
from .. import Item

K_VALUE="value"
K_PREPEND="prepend"

class Scalar(Arguments.Argument):
    def __init__(self, value, prepend=None, name=None, prefix=None, metadata_rules=None):
        super().__init__(name, prefix, metadata_rules)
        self.value = value
        self.prepend = prepend

    def __deepcopy__(self, memodict={}):
        return Scalar(self.value, self.prepend, self.name, self.prefix, self.metadata_rules)

    def _loop(self, command_set):
        logging.log(6, "Looping Scalar:{}/{}".format(self.name,self.prefix))
        v = self.value if not self.prepend else os.path.join(self.prepend, self.value)
        for item in Arguments._generate(command_set):
            yield item, v

    def _apply(self, item, value):
        return Item._apply_argument_to_item(item, self.name, self.prefix, value)

    def to_dict(self):
        d = super().to_dict()
        d[K_VALUE] = self.value
        d[K_PREPEND] = self.prepend
        return d

    @classmethod
    def from_dict(cls, d):
        return Scalar(d.get(K_VALUE),
                    d.get(K_PREPEND),
                    name = d.get(Arguments.K_NAME),
                    prefix = d.get(Arguments.K_PREFIX),
                    metadata_rules = d.get(Arguments.K_METADATA_RULES))