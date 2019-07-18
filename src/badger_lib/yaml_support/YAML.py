__author__ = "alvaro barbeira"

import collections
import copy
import os
import logging

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ..arguments import Arguments
from ..arguments import Scalar
from ..arguments import FilesInFolder
from ..arguments import RulesMap
from ..arguments import ArgumentFromMetadata
from ..arguments import Whitelist
from ..arguments import Blacklist
from ..arguments import Range

from ..submission import PBSQueue

from .. import Configuration

########################################################################################################################
def argument_representer(dumper, data):
    return dumper.represent_mapping(data.to_dict())

def _constructor(cls, loader, node):
    d = loader.construct_mapping(node)
    return  cls.from_dict(d)

########################################################################################################################
INITIALIZED=False

def initialize_yaml():
    global INITIALIZED
    if INITIALIZED:
        return
    """Not really meant for use. Mostly, an interactive running convenience.."""
    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

    def dict_representer(dumper, data):
        return dumper.represent_dict(data.iteritems())

    def dict_constructor(loader, node):
        return collections.OrderedDict(loader.construct_pairs(node))

    yaml.add_representer(collections.OrderedDict, dict_representer)
    yaml.add_constructor(_mapping_tag, dict_constructor, yaml.SafeLoader)
    #
    yaml.add_representer(u"!PBSQueue", argument_representer)
    yaml.add_constructor(u"!PBSQueue", lambda loader, node: _constructor(PBSQueue.PBSQueueSubmission, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!MetadataOperation", argument_representer)
    yaml.add_constructor(u"!MetadataOperation", lambda loader, node: _constructor(Arguments.MetadataOperation, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!SaveValueInMetadata", argument_representer)
    yaml.add_constructor(u"!SaveValueInMetadata", lambda loader, node: _constructor(Arguments.SaveValueInMetadata, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!SaveToMetadata", argument_representer)
    yaml.add_constructor(u"!SaveToMetadata", lambda loader, node: _constructor(Arguments.SaveToMetadata, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!ExtractFromValueWithRegexpMetadata", argument_representer)
    yaml.add_constructor(u"!ExtractFromValueWithRegexpMetadata", lambda loader, node: _constructor(Arguments.ExtractFromValueWithRegexpMetadata, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!MapMetadataValue", argument_representer)
    yaml.add_constructor(u"!MapMetadataValue", lambda loader, node: _constructor(Arguments.MapMetadataValue, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!Scalar", argument_representer)
    yaml.add_constructor(u"!Scalar", lambda loader, node: _constructor(Scalar.Scalar, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!ArgumentFromMetadata", argument_representer)
    yaml.add_constructor(u"!ArgumentFromMetadata", lambda loader, node: _constructor(ArgumentFromMetadata.ArgumentFromMetadata, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!FilesInFolder", argument_representer)
    yaml.add_constructor(u"!FilesInFolder", lambda loader, node: _constructor(FilesInFolder.FilesInFolder, loader, node), yaml.SafeLoader)

    yaml.add_representer(u"!ExtractFromFileNameRegexpMetadata", argument_representer)
    yaml.add_constructor(u"!ExtractFromFileNameRegexpMetadata", lambda loader, node: _constructor(FilesInFolder.ExtractFromFileNameRegexpMetadata, loader, node), yaml.SafeLoader)
    #
    yaml.add_representer(u"!RulesMap", argument_representer)
    yaml.add_constructor(u"!RulesMap", lambda loader, node: _constructor(RulesMap.RulesMap, loader, node), yaml.SafeLoader)

    yaml.add_representer(u"!RulesMapGetKeyMetadata", argument_representer)
    yaml.add_constructor(u"!RulesMapGetKeyMetadata", lambda loader, node: _constructor(RulesMap.RulesMapGetKeyMetadata, loader, node), yaml.SafeLoader)

    yaml.add_representer(u"!Whitelist", argument_representer)
    yaml.add_constructor(u"!Whitelist", lambda loader, node: _constructor(Whitelist.Whitelist, loader, node), yaml.SafeLoader)

    yaml.add_representer(u"!Blacklist", argument_representer)
    yaml.add_constructor(u"!Blacklist", lambda loader, node: _constructor(Blacklist.Blacklist, loader, node), yaml.SafeLoader)

    yaml.add_representer(u"!Range", argument_representer)
    yaml.add_constructor(u"!Range", lambda loader, node: _constructor(Range.Range, loader, node), yaml.SafeLoader)


    INITIALIZED=True

def _patch(configuration, sub):
    if type(configuration) == list and type(sub) == list:
        n = copy.deepcopy(configuration)
        n.extend(sub)
        return n
    elif type(configuration) == collections.OrderedDict and type(sub) == collections.OrderedDict:
        n = copy.deepcopy(configuration)
        for k,v in sub.items():
            if k in n:
                n[k] = _patch(n[k], v)
            else:
                n[k] = copy.deepcopy(v)
        return n

    return copy.deepcopy(sub)

def _flatify_import(configuration):
    if not Configuration.K_SUBCONFIGURATION in configuration:
        return configuration

    c = copy.deepcopy(configuration)

    subs = c.pop(Configuration.K_SUBCONFIGURATION)
    args = c.pop(Configuration.K_ARGUMENTS)

    #TODO: formalize the following case into a class?
    sub_pre_argument = [x for x in subs if  x["how"] == "before_arguments"]
    base_path = Configuration._base_path(configuration)

    for x in sub_pre_argument:
        logging.info("Preloading %s", x)
        p = os.path.join(base_path, x["path"])
        with open(p) as f:
            sub = yaml.safe_load(f)
        c = _patch(c, sub)

    if Configuration.K_ARGUMENTS in c:
        c[Configuration.K_ARGUMENTS] = _patch(c[Configuration.K_ARGUMENTS], args)
    else:
        c[Configuration.K_ARGUMENTS] = args
    return c

def load_yaml(path):
    with open(path) as f:
        configuration = yaml.safe_load(f)
    configuration[Configuration.K_CONFIGURATION_SOURCE] = path
    configuration = _flatify_import(configuration)
    return configuration