__author__ = "alvaro barbeira"
import copy
import re
from collections import OrderedDict

from . import  Configuration

K_UNNAMED="__unnamed"
K_METADATA="metadata"
#TODO: this has to go in Item/Configuration refactor
K_CONFIGURATION_BASE_PATH="__configuration_path"
K_CONFIGURATION="__configuration"

def _template(configuration):
    instruction = configuration[Configuration.K_DEFINITIONS][Configuration.K_COMMAND]
    t = OrderedDict([(Configuration.K_COMMAND, instruction),
                     (Configuration.K_ARGUMENTS, OrderedDict()),
                     (K_METADATA, OrderedDict([(K_CONFIGURATION_BASE_PATH, Configuration._base_path(configuration))])),
                     ])

    # t = {Configuration.K_COMMAND: instruction,
    #     Configuration.K_ARGUMENTS: {},
    #     K_METADATA: {K_CONFIGURATION_BASE_PATH: Configuration._base_path(configuration)},
    # }

    if Configuration.K_COPY_TO_ITEM in configuration[Configuration.K_DEFINITIONS] and configuration[Configuration.K_DEFINITIONS][Configuration.K_COPY_TO_ITEM]:
        t[K_METADATA][K_CONFIGURATION] = configuration
    return t


def _copy(item):
    i = OrderedDict()
    for k,v in item.items():
        #Shallow copy
        _type = type(v)
        if k == K_METADATA:
            _c = {}
            for _k, _v in v.items():
                if _k == K_CONFIGURATION:
                    _c[_k] = _v
                else:
                    _c[_k] = copy.deepcopy(_v)
            i[k] = _c
        else:
            i[k] = copy.deepcopy(v)
    return i

def _path(path):
    return path.split("/")

def _path_target(path):
    path = _path(path)
    if len(path) == 1:
        target = path[0]
        path = None
    else:
        target = path[-1]
        path = path[:-1]
    return path, target


def _has_metadata(item, path):
    m = item[K_METADATA]
    path = _path(path)
    for p in path:
        if not p in m:
            return False
        m = m[p]
    return True

def _get_metadata(item, path=None):
    m = item[K_METADATA]
    if path:
        if type(path) == str:
            path = _path(path)
        for p in path:
            if not p in m:
                m[p] = {}
            m = m[p]
    return m

def _add_key_value_to_metadata(item, path, value, override=False):
    _path, _target = _path_target(path)
    m = _get_metadata(item, _path)
    if _target in m and not override:
        raise RuntimeError("metadata target path is already defined.")
    m[_target] = value

def _argument_key(name, prefix):
    if not name and prefix:
        key = prefix
        while _dash_re.search(key):
            key = _dash_re.sub("", key)
    elif not name and not prefix:
        key = K_UNNAMED
    else:
        key = name
    return key

_dash_re = re.compile("^-")
def _apply_argument_to_item(item, name, prefix,  value):
    key = _argument_key(name, prefix)

    item = _copy(item)
    arguments = item[Configuration.K_ARGUMENTS]

    if not name in arguments:
        arguments[key] = []

    arguments[key].append((prefix, value))

    return item

def _get_argument_value(item, key, how="first"):
    if how == "first":
        return  item[Configuration.K_ARGUMENTS][key][0][1]
    else:
        raise RuntimeError("Implement!")

def _argumentize_prefixed(key, values):
    _v = []
    for prefix, value in values:
        if prefix: _v.append(prefix)
        #TODO: maybe this is wrong.
        if value: _v.append(str(value))

    _v = " ".join(_v)
    return key, _v

