#!/usr/bin/python2.7

"""Decide what to do, then run the relevant file."""

import sys
#import autotag
import import_tracks
import yaml
import argparse

config = "./config.yaml"

def main(argv):
    conf = yaml.safe_load(open(config))
    parser = argparse.ArgumentParser(description = "Do stuff with music files.")
    parser.add_argument('action', action="store", choices=["import"],
        help="import: import the files")
    args = vars(parser.parse_args(argv))
    if args["action"] == "import":
        import_tracks.main(argv[1:], conf)

if(__name__ == "__main__"):
    main(sys.argv[1:])