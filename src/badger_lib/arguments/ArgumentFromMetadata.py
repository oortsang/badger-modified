__author__ = "alvaro barbeira"

import logging
import os
import copy

from . import Arguments
from .. import Item

K_SOURCES="sources"
K_PREPEND="prepend"
K_FORMAT_RULE="format_rule"
K_OPTIONS="options"
K_OPTIONS_FROM_METADATA_PATH="options_from_metadata_path"
K_SUB_KEY="sub_key"
K_PATH="path"
#There is a key like this one in another semantics. Should we unify?
K_DESTINATION="destination"
K_DEFAULT="__default"

class ArgumentFromMetadata(Arguments.Argument):
    def __init__(self, sources, prepend, format_rule, options, options_from_metadata_path, sub_key, name=None, prefix=None, metadata_rules=None):
        super().__init__(name, prefix, metadata_rules)
        self.sources = sources
        self.prepend = prepend
        self.format_rule = format_rule
        self.options = options
        self.options_from_metadata_path = options_from_metadata_path
        self.sub_key = sub_key

    def __deepcopy__(self, memodict={}):
        return  ArgumentFromMetadata(self.sources, self.prepend, self.format_rule, self.options, self.options_from_metadata_path, self.sub_key, self.name, self.prefix, self.metadata_rules)

    def _loop(self, command_set):
        logging.log(6, "Looping ArgumentFromMetadata:{}".format(self.name))
        for item in Arguments._generate(command_set):
            options = None
            if self.options:
                options = self.options
            elif self.options_from_metadata_path:
                options = Item._get_metadata(item, self.options_from_metadata_path)

            f = self.format_rule
            if self.prepend:
                f = os.path.join(self.prepend, self.format_rule)
            value = _get_value(item, self.sources, f, options, self.sub_key)
            # TODO: make the -missing values handling- optionally lenient

            #if value and self.prepend:
            #    value = os.path.join(self.prepend, value)
            yield item, value

    def _apply(self, item, value):
        if not value:
            return Item._copy(item)
        return Item._apply_argument_to_item(item, self.name, self.prefix, value)

    def to_dict(self):
        d = super().to_dict()
        d[K_SOURCES] = self.sources
        d[K_PREPEND] = self.prepend
        d[K_FORMAT_RULE] = self.format_rule
        d[K_OPTIONS] = self.options
        d[K_OPTIONS_FROM_METADATA_PATH] = self.options_from_metadata_path
        d[K_SUB_KEY] = self.sub_key
        return d

    @classmethod
    def from_dict(cls, d):
        return ArgumentFromMetadata(d.get(K_SOURCES), d.get(K_PREPEND), d.get(K_FORMAT_RULE), d.get(K_OPTIONS),
                                    d.get(K_OPTIONS_FROM_METADATA_PATH), d.get(K_SUB_KEY),
                       name = d.get(Arguments.K_NAME),
                       prefix = d.get(Arguments.K_PREFIX),
                       metadata_rules = d.get(Arguments.K_METADATA_RULES))

def _get_value(item, sources, format_rule, options, sub_key):
    if format_rule: return _get_value_f(item, sources, format_rule)
    return _get_value_o(item, sources, options, sub_key)

def _get_value_f(item, sources, format_rule):
    for source in sources:
        if not Item._has_metadata(item, source[K_PATH]):
            return None
    v = {source[K_DESTINATION]: Item._get_metadata(item, source[K_PATH]) for source in sources}
    return format_rule.format(**v)

def _get_value_o(item, sources, options, sub_key):
    if len(sources) != 1:
        raise RuntimeError("ArgumentFromMetadata with option: only one source must be specified")

    k = [source[K_PATH] for source in sources][0]
    if not Item._has_metadata(item, k):
        return None
    v = Item._get_metadata(item, k)
    r = None
    if sub_key:
        if v in options and sub_key in options[v]:
            r = options[v][sub_key]
        elif K_DEFAULT in options and sub_key in options[K_DEFAULT]:
            r = options[K_DEFAULT][sub_key]
    else:
        if v in options:
            r = options[v]
        elif K_DEFAULT in options:
            r = options[K_DEFAULT]
    return r