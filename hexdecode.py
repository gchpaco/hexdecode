from __future__ import annotations
import revealparser
import kjsparser
import argparse
import json
import pickle
import fileinput
from hexast import massage_raw_pattern_list, PatternRegistry
import signal
import sys

# don't show KeyboardInterrupt traceback on ctrl+c
signal.signal(signal.SIGINT, lambda a, b: sys.exit(1))

parser = argparse.ArgumentParser()
parser.add_argument('registry', help="Pattern registry to use")
parser.add_argument('translations', help="Translation table to use", default=None, nargs="?")
parser.add_argument('--kubejs',
                    help="Use kubejs parser",
                    action='store_true')
parser.add_argument('--highlight',
                    help="Whether or not to highlight the structure",
                    action='store_true')

if __name__ == "__main__":
    args = parser.parse_args()

    with open(args.registry, "rb") as file:
        registry: PatternRegistry = pickle.load(file)

    if args.translations:
        with open(args.translations, "r") as file:
            translation_table = json.load(file)
    else:
        translation_table = {}

    if args.kubejs:
        for line in fileinput.input(files=[], encoding="utf-8"):
            for page_name, iotas in kjsparser.parse(line):
                print("===", page_name, "===")
                level = 0
                for iota in massage_raw_pattern_list(iotas, registry):
                    level = iota.preadjust(level)
                    iota.print(level, args.highlight, translation_table)
                    level = iota.postadjust(level)
    else:
        for line in fileinput.input(files=[], encoding="utf-8"):
            level = 0
            for pattern in revealparser.parse(line):
                for iota in massage_raw_pattern_list(pattern, registry):
                    level = iota.preadjust(level)
                    iota.print(level, args.highlight, translation_table)
                    level = iota.postadjust(level)
