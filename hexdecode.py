from __future__ import annotations
from parser import parse
import argparse
import json
import fileinput

parser = argparse.ArgumentParser()
parser.add_argument('registry', help="Pattern registry to use", type=open)
parser.add_argument('--highlight',
                    help="Whether or not to highlight the structure",
                    action='store_true')

if __name__ == "__main__":
    args = parser.parse_args()

    pattern_registry = json.load(args.registry)

    for line in fileinput.input(files=[], encoding="utf-8"):
        level = 0
        for iota in parse(line, pattern_registry):
            level = iota.preadjust(level)
            iota.print(level, args.highlight)
            level = iota.postadjust(level)
