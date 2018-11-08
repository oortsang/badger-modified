__author__ = "alvaro barbeira"
import logging
from . import Arguments
from .. import Item

########################################################################################################################

K_RULES="rules"

class RulesMap(Arguments.Argument):
    def __init__(self, rules, name=None, prefix=None, metadata_rules=None):
        super().__init__(name, prefix, metadata_rules)
        self.rules = rules

    def __deepcopy__(self, memodict={}):
        return RulesMap(self.rules, self.name, self.prefix, self.metadata_rules)

    def apply(self, command_set):
        logging.log(6, "Looping RulesMap:{}".format(self.name))
        c = []
        for key, rules in self.rules.items():
            # Todo: metadata rules
            _c = command_set
            for rule in rules:
                if isinstance(rule, Arguments.Argument):
                    _c = rule.apply(_c)
            for item in _c:
                if self.metadata_rules:
                    for metadata_rule in self.metadata_rules:
                        metadata_rule(item, self, None, key=key, rules=rules)
                yield item

    def to_dict(self):
        d = super().to_dict()
        d[K_RULES] = self.rules
        return d

    @classmethod
    def from_dict(cls, d):
        return RulesMap(d.get(K_RULES),
                        name = d.get(Arguments.K_NAME),
                        prefix = d.get(Arguments.K_PREFIX),
                        metadata_rules = d.get(Arguments.K_METADATA_RULES))


########################################################################################################################

class RulesMapGetKeyMetadata(Arguments.MetadataRule):
    def __call__(self, item, argument, value, *args, **kwargs):
        Item._add_key_value_to_metadata(item, self.path, kwargs["key"])

    def __deepcopy__(self, memodict={}):
        return RulesMapGetKeyMetadata(self.name, self.path)

    @classmethod
    def from_dict(cls, d):
        return RulesMapGetKeyMetadata(name=d.get(Arguments.K_NAME), path=d.get(Arguments.K_PATH))


