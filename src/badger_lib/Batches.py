__author__ = "alvaro barbeira"

import logging
import os
import re
from collections import OrderedDict
from subprocess import call

from . import Item, Configuration
from badger_lib.yaml_support import YAML

########################################################################################################################

#TODO abstract away
import jinja2
#shamelessly derived from http://matthiaseisen.com/pp/patterns/p0198/
def get_template(configuration):
    path = Configuration._template_path(configuration)
    path, filename = os.path.split(path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename)

########################################################################################################################

def process(configuration_path, page_width=None, page=None):
    #Todo: reentrant initialization?
    YAML.initialize_yaml()
    configuration = YAML.load_yaml(configuration_path)
    _process(configuration, page_width, page)

def _parse_configuration(configuration):
    template = Item._template(configuration)

    arguments = configuration[Configuration.K_ARGUMENTS]
    command_set = [template]
    for argument in arguments:
        logging.info("Applying argument %s", argument.name if argument.name else "unnamed")
        command_set = [x for x in argument.apply(command_set)]

    return command_set

#Todo: maybe move to item
def _to_template_arguments(item, configuration):
    d = OrderedDict()

    if Configuration.K_COMMAND in configuration[Configuration.K_DEFINITIONS]:
        d[Configuration.K_COMMAND] = configuration[Configuration.K_DEFINITIONS][Configuration.K_COMMAND]

    if Configuration.K_DEFAULT_ARGUMENTS in configuration[Configuration.K_DEFINITIONS]:
        d = { **d, **(configuration[Configuration.K_DEFINITIONS][Configuration.K_DEFAULT_ARGUMENTS])}

    arguments = item[Configuration.K_ARGUMENTS]
    for key, values in arguments.items():
        key, value = Item._argumentize_prefixed(key, values)
        d[key] = value

    return d

r_ = re.compile(r"\\\n[\s]+\\\n")
def _render(item, configuration, template):
    t = _to_template_arguments(item, configuration)
    r = template.render(t)
    while r_.search(r):
        r = r_.sub("\\\n",r) #substitute empty lines on missing values
    return r

def _crude_render(command):
    c = command[Configuration.K_COMMAND]
    for prefix, value in command[Configuration.K_ARGUMENTS].items():
        if prefix == Item.K_UNNAMED:
            c += " " + value
        else:
            c += " {} {}".format(prefix, value)
    c += "\n"
    return c

def _process(configuration, page_width=None, page=None):
    if Configuration.K_PRE_COMMAND in configuration[Configuration.K_DEFINITIONS]:
        pre = configuration[Configuration.K_DEFINITIONS][Configuration.K_PRE_COMMAND]
        for p in pre:
            call(p, shell=True)

    logging.info("Parsing configuration")
    command_set = _parse_configuration(configuration)
    logging.info("%d commands generated", len(command_set))

    logging.info("Loading template")
    template = get_template(configuration)

    if page_width is not None and page is not None:
        start_index = page_width * page
        end_index = start_index + page_width
    else:
        start_index = None
        end_index = None

    logging.info("Submitting...")
    submission = configuration[Configuration.K_DEFINITIONS][Configuration.K_SUBMISSION]
    submitted =[]
    for i, item in enumerate(command_set):
        if start_index is not None and i<start_index:
            logging.log(8, "Skipping job %i", i)
            continue
        if end_index is not None and i==end_index:
            logging.log(8, "Breaking at job %i", i)
            break
        #todo: name
        item_render = _render(item, configuration, template)
        item = submission.submit(item, item_render, configuration)
        submitted.append(item)
        #TODO: clean up lookup
        logging.log(9, "Submitted job: %s", submission.explain(item))

    logging.info("Submitted")