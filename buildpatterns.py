import re
import pickle
import glob
from hexast import Direction, get_rotated_pattern_segments, PatternRegistry
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("registry", help="The filename to write the registry to")
parser.add_argument("files", help="The .java files to parse the registry from", nargs="*")

registry_regex = re.compile(r"PatternRegistry\s*\.\s*mapPattern\s*\(\s*HexPattern\s*\.\s*fromAngles\s*\(\s*\"([aqwed]+)\"\s*,\s*HexDir\s*\.\s*(\w+)\s*\)\s*,\s*modLoc\s*\(\s*\"([\w/]+)\"\s*\).+?(true)?\);", re.M | re.S)

if __name__ == "__main__":
    args = parser.parse_args()

    registry = PatternRegistry()
    for path in args.files:
        for filename in glob.glob(path):
            with open(filename, "r", encoding="utf-8") as file:
                for match in registry_regex.finditer(file.read()):
                    (pattern, direction, name, is_great) = match.groups()
                    if is_great:
                        for segments in get_rotated_pattern_segments(Direction[direction], pattern):
                            registry.great_spells[segments] = name
                    else:
                        registry.spells[pattern] = name

    with open(args.registry, "wb") as file:
        pickle.dump(registry, file)

    print(f"Successfully wrote pattern registry to {args.registry}")
