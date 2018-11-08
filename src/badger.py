#!/usr/bin/env python
__author__ = "alvaro barbeira"


from badger_lib import Batches, Logging

def run(args):
    #todo maybe configuration format should be optional
    Batches.process(args.yaml_configuration_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Generate batch files from configuration")
    parser.add_argument("-yaml_configuration_file", help="Read configuration from yaml file")
    parser.add_argument("-parsimony",
                        help="Log parsimony level. 1 is everything being logged. 10 is only high level messages, above 10 will hardly log anything",
                        type=int, default=10)
    args = parser.parse_args()

    Logging.configure_logging(args.parsimony)

    run(args)