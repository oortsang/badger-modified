#!/usr/bin/env python
__author__ = "alvaro barbeira"


# import sys, os, importlib.util
# def module_importer(module_name, target_path):
#     # See https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
#     target_path = os.path.abspath(os.path.expanduser(target_path))
#     spec = importlib.util.spec_from_file_location(module_name, target_path)
#     module = importlib.util.module_from_spec(spec)
#     sys.modules[module_name] = module
#     spec.loader.exec_module(module)
#     return module

# # badger_lib = module_importer("badger_lib", f"{os.cwd()}badger_lib/__init__.py")
# from . import badger_lib
from badger_lib import Batches, Logging
from typing import List

def run(args):
    #todo maybe configuration format should be optional
    return Batches.process(
        args.yaml_configuration_file,
        args.page_width,
        args.page
    )

def run_from_python(
        yaml_config_file,
        parsimony=10,
        silence: bool = False,
        page_width=None,
        page=None
) -> List[str]:
    """Helper function to make it easier to call badger from python"""
    if not silence:
        Logging.configure_logging(parsimony)

    # import pdb; pdb.set_trace()
    return Batches.process(
        yaml_config_file,
        page_width,
        page
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Generate batch files from configuration")
    parser.add_argument("-yaml_configuration_file", help="Read configuration from yaml file")
    parser.add_argument("-parsimony", help="Log parsimony level. 1 is everything being logged. 10 is only high level messages, above 10 will hardly log anything", type=int, default=8)
    parser.add_argument("--page_width", help="split the jobs into pages of this width", type=int)
    parser.add_argument("--page", help="run only this page of jobs", type=int)

    args = parser.parse_args()

    Logging.configure_logging(args.parsimony)

    run(args)
