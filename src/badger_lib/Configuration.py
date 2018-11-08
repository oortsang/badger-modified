__author__ = "alvaro barbeira"

import os

K_DEFINITIONS="definitions"
K_ARGUMENTS="arguments"

K_DESTINATION="destination"
K_PRE_COMMAND="pre_command"
K_COMMAND="command"
K_TEMPLATE="template"
K_SUBCONFIGURATION="sub_configuration"
K_DEFAULT_ARGUMENTS="default_arguments"
K_SUBMISSION="submission"
K_CONFIGURATION_SOURCE="__configuration_source"
K_COPY_TO_ITEM="copy_to_item"

def path_based_on_configuration(configuration, path):
    if os.path.isabs(path):
        return path
    r = _base_path(configuration)
    return os.path.join(r, path)

def _base_path(configuration):
    return os.path.split(configuration[K_CONFIGURATION_SOURCE])[0]

def _template_path(configuration):
    return path_based_on_configuration(configuration, configuration[K_DEFINITIONS][K_TEMPLATE])
