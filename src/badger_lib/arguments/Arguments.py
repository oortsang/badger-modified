__author__ = "alvaro barbeira"

import copy
import logging
import re
import os

from .. import Item

K_NAME="name"
K_PREFIX="prefix"
K_METADATA_RULES="metadata_rules"

########################################################################################################################
# Argument hierarchy root
class Argument:
    def __init__(self, name=None, prefix=None, metadata_rules=None):
        self.name = name
        self.prefix = prefix
        self.metadata_rules = metadata_rules

    def __deepcopy__(self, memodict={}):
        raise RuntimeError("Not implemented")

    def apply(self, command_set):
        for item, values in self._loop(command_set):
            item = self._apply(item, values)
            if self.metadata_rules:
                for rule in self.metadata_rules:
                    item = Item._copy(item)
                    rule(item, self, values)
            yield item

    def name_prefix_pair(self):
        return self.name, self.prefix

    def _loop(self, command_set): raise RuntimeError("Not implemented")
    def _apply(self, item, args): raise RuntimeError("Not implemented")

    def to_dict(self):
        return {K_NAME: self.name, K_PREFIX:self.prefix, K_METADATA_RULES:self.metadata_rules}

    @classmethod
    def from_dict(cls, d): raise RuntimeError("Not implemented")


def _generate(command_set):
    for item in command_set:
        yield Item._copy(item)

########################################################################################################################
#Metadata hierarchy root
K_PATH="path"

#TODO: name and path are not really necessary; path for sure is not.
class MetadataRule:
    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path

    def __deepcopy__(self, memodict={}):
        return MetadataRule(self.name, self.path)

    def __call__(self, item, argument, values, *args, **kwargs): raise RuntimeError("Not implemented")

    def to_dict(self):
        return {K_NAME: self.name, K_PATH:self.path}

    @classmethod
    def from_dict(cls, d): raise RuntimeError("Not implemented")

########################################################################################################################
#maybe move to its own module

class SaveValueInMetadata(MetadataRule):
    def __init__(self, name=None, path=None):
        super().__init__(name, path)


    def __deepcopy__(self, memodict={}):
        return SaveValueInMetadata(self.name, self.path)

    def __call__(self, item, argument,value, *args, **kwargs):
        Item._add_key_value_to_metadata(item, self.path, value)

    def to_dict(self):
        d = super().to_dict()
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d.get(K_NAME), d.get(K_PATH))

K_REGEXP="regexp"
K_STRICT="strict"

class ExtractFromValueWithRegexpMetadata(MetadataRule):
    def __init__(self, regexp, strict, name=None, path=None):
        super().__init__(name, path)
        self.strict = strict
        self.regexp = re.compile(regexp) if regexp else None

    def __deepcopy__(self, memodict={}):
        return ExtractFromValueWithRegexpMetadata(self.regexp.pattern, self.strict, self.name, self.path)

    def __call__(self, item, argument,value, *args, **kwargs):
        logging.log(5, "Extracting {} from {}".format(self.regexp.pattern, value))
        if not self.regexp:
            raise RuntimeError("Regular expression must be initialized before calling extraction")
        s = self.regexp.search(value)
        if self.strict and not s:
            raise RuntimeError("Metadata extract operation failed in strict mode")

        if s:
            v = s.group(1)
            Item._add_key_value_to_metadata(item, self.path, v)

    def to_dict(self):
        d = super().to_dict()
        d[K_REGEXP] = self.regexp.pattern
        d[K_STRICT] = self.strict
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d.get(K_REGEXP), d.get(K_STRICT), name=d.get(K_NAME), path=d.get(K_PATH))

K_FROM_METADATA_PATH = "from_metadata_path"
K_TO_METADATA_PATH = "to_metadata_path"
K_USING_MAP = "using_map"
K_FORGIVING = "forgiving"

# TODO: refactor with configuration/formalization
import yaml

class MapMetadataValue(MetadataRule):
    def __init__(self, from_metadata_path, to_metadata_path, using_map, forgiving=None, name=None, path=None):
        super().__init__(name, path)
        self.from_metada_path = from_metadata_path
        self.to_metadata_path = to_metadata_path
        self.using_map = using_map
        self.forgiving = forgiving
        self._map = None

    def __deepcopy__(self, memodict={}):
        return MapMetadataValue(self.from_metada_path, self.to_metadata_path, self.using_map, self.forgiving, self.name, self.path)

    def __call__(self, item, argument, value,  *args, **kwargs):
        k = Item._get_metadata(item, self.from_metada_path)
        #Load it only once
        if not self._map:
            if isinstance(self.using_map, dict):
                self._map = self.using_map
            else:
                #TODO: refactor, remove yaml dependency
                p = _get_sub(item, self.using_map)
                with open(p) as f:
                    self._map = yaml.load(f)

        if self.forgiving:
            if not k in self._map:
                return
        v = self._map[k]
        Item._add_key_value_to_metadata(item, self.to_metadata_path, v)

    def to_dict(self):
        d = super().to_dict()
        d[K_FROM_METADATA_PATH] = self.from_metada_path
        d[K_TO_METADATA_PATH] = self.to_metadata_path
        d[K_USING_MAP] = self.using_map
        d[K_FORGIVING] = self.forgiving
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d.get(K_FROM_METADATA_PATH), d.get(K_TO_METADATA_PATH), d.get(K_USING_MAP), d.get(K_FORGIVING), name=d.get(K_NAME), path=d.get(K_PATH))

K_KEY="key"
K_VALUE="value"

class SaveToMetadata(MetadataRule):
    def __init__(self, key, value, name=None, path=None):
        super().__init__(name, path)
        self.key = key
        self.value = value

    def __deepcopy__(self, memodict={}):
        return SaveValueInMetadata(self.key, self.value, self.name, self.path)

    def __call__(self, item, argument, value, *args, **kwargs):
        Item._add_key_value_to_metadata(item, self.key, self.value)

    def to_dict(self):
        d = super().to_dict()
        d[K_KEY] = self.key
        d[K_VALUE] = self.value
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(d.get(K_KEY), d.get(K_VALUE), d.get(K_NAME), d.get(K_PATH))

########################################################################################################################

class MetadataOperation(Argument):
    def __init__(self, metadata_rules=None):
        super().__init__(None, None, metadata_rules)

    def __deepcopy__(self, memodict={}):
        return MetadataOperation(self.metadata_rules)

    def _loop(self, command_set):
        logging.log(7, "Looping Metadata Operation:{}/{}".format(self.name,self.prefix))
        for item in _generate(command_set):
            yield item, None

    def _apply(self, item, value):
        return item

    def to_dict(self):
        d = super().to_dict()
        return d

    @classmethod
    def from_dict(cls, d):
        return MetadataOperation(metadata_rules = d.get(K_METADATA_RULES))

#this has to go too
def _get_sub(item, path):
    if os.path.isabs(path):
        return path
    return os.path.join(Item._get_metadata(item, Item.K_CONFIGURATION_BASE_PATH), path)


def _load(file):
    r=[]
    with open(file) as f:
        for line in f:
            entry = line.strip()
            if entry[0] == "#": continue
            r.append(line.strip())
    return r