from __future__ import annotations
import regex
import argparse
from typing import Literal
from enum import Enum
import json
import fileinput

# working as of https://github.com/gamma-delta/HexMod/blob/c00815b7b9d90593dc33e3a7539ce87c2ece4fc9/Common/src/main/java/at/petrak/hexcasting/common/casting/RegisterPatterns.java

# setup:
# - run "pip install regex"
# - download this script somewhere
# - go to https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/java/at/petrak/hexcasting/common/casting/RegisterPatterns.java
# - right click the "Raw" button, click "Save Link As", and save it with the name "RegisterPatterns.java" to the same folder as this script
#   - note: you'll have to do this again after each update, if new patterns are added or old patterns are changed

# usage:
# - put your hex on the stack
# - cast Reveal
# - open <game folder>/logs/latest.log, scroll to the bottom, and copy your hex
# - paste your hex inside the quotes on the following line (it should look like this: data = "[HexPattern(...), HexPattern(...)]")
data = ""
# - save and run the script

regexes = {
    "list_iota": regex.compile(r"\s*\[(.*)\]\s*"),
    "list_iota_item": regex.compile(r"(\[(?>[^\[\]]+|(?R))*\]|[^,]+)(?:, )?"),
    "pattern_iota": regex.compile(r"HexPattern\((\w+)(?: ([aqwed]+))?\)"),
    "number_constant": regex.compile(r"\d+(?:\.\d+)?"),
}

class Angle(Enum):
    FORWARD    = 0
    w          = 0
    RIGHT      = 1
    e          = 1
    RIGHT_BACK = 2
    d          = 2
    BACK       = 3
    LEFT_BACK  = 4
    a          = 4
    LEFT       = 5
    q          = 5

class Direction(Enum): # numbers increase clockwise
    NORTH_EAST = 0
    EAST       = 1
    SOUTH_EAST = 2
    SOUTH_WEST = 3
    WEST       = 4
    NORTH_WEST = 5

    def angle_from(self, other: Direction) -> Angle:
        return Angle((self.value - other.value) % len(Angle))

    def rotated(self, angle: str | Angle) -> Direction:
        offset = Angle[angle].value if type(angle) is str else angle.value
        return Direction((self.value + offset) % len(Direction))

class Iota:
    def __init__(self, datum):
        self._datum = datum
    def color(self) -> str:
        return ""
    def print(self, level: int, highlight: bool):
        indent = "  " * level
        if highlight:
            print(indent + self.color() + self._datum + "\033[00m")
        else:
            print(indent + self._datum)
    def preadjust(self, level: int) -> int:
        return level
    def postadjust(self, level: int) -> int:
        return level

class ListOpener(Iota):
    def postadjust(self, level: int) -> int:
        return level + 1

class ListCloser(Iota):
    def preadjust(self, level: int) -> int:
        return level - 1

class Pattern(Iota):
    def color(self):
        return "\033[93m" # yellow

class PatternOpener(Pattern):
    def postadjust(self, level: int) -> int:
        return level + 1

class PatternCloser(Pattern):
    def preadjust(self, level: int) -> int:
        return level - 1

class NumberConstant(Iota):
    def color(self):
        return "\033[92m" # light green

class Unknown(Iota):
    def color(self):
        return "\033[91m" # light red

def get_pattern_directions(starting_direction: Direction, pattern: str) -> list[Direction]:
    directions = [starting_direction]
    for c in pattern:
        directions.append(directions[-1].rotated(c))
    return directions

def parse_mask(starting_direction: Direction, pattern: str) -> str | None:
    if not pattern:
        return "⁻"
    directions = get_pattern_directions(starting_direction, pattern)
    flat_direction = starting_direction.rotated(Angle.LEFT) if pattern[0] == "a" else starting_direction
    mask = ""
    skip = False
    for index, direction in enumerate(directions):
        if skip:
            skip = False
            continue
        angle = direction.angle_from(flat_direction)
        if angle == Angle.FORWARD:
            mask += "⁻"
            continue
        if index >= len(directions) - 1:
            return None
        angle2 = directions[index + 1].angle_from(flat_direction)
        if angle == Angle.RIGHT and angle2 == Angle.LEFT:
            mask += "v"
            skip = True
            continue
        return None
    return mask

def parse_iota(registry, iota: str):
    list_contents_match = regexes["list_iota"].fullmatch(iota)

    if list_contents_match:
        list_contents = list_contents_match.group(1)
        yield ListOpener("[")
        for item_match in regexes["list_iota_item"].finditer(list_contents):
            yield from parse_iota(registry, item_match.group(1))
        yield ListCloser("]")
    else:
        pattern_match = regexes["pattern_iota"].fullmatch(iota)
        if pattern_match:
            direction = Direction[pattern_match.group(1)]
            pattern = pattern_match.group(2) or ""
            name = registry.get(pattern)
            mask = parse_mask(direction, pattern)

            if name:
                if name == "open_paren":
                    yield PatternOpener("{")
                elif name == "close_paren":
                    yield PatternCloser("}")
                else:
                    yield Pattern(name)

            elif mask:
                yield Pattern(f"mask {mask}")

            elif pattern.startswith(("aqaa", "dedd")):
                negate = pattern.startswith("dedd")
                accumulator = 0.
                for c in pattern[4:]:
                    match c:
                        case "w":
                            accumulator += 1
                        case "q":
                            accumulator += 5
                        case "e":
                            accumulator += 10
                        case "a":
                            accumulator *= 2
                        case "d":
                            accumulator /= 2
                if negate:
                    accumulator = -accumulator
                yield Pattern(f"number {str(accumulator).rstrip('0').rstrip('.')}")

            else:
                yield Pattern('unknown')
        else:
            if regexes["number_constant"].fullmatch(iota):
                yield NumberConstant(iota)
            else:
                yield Unknown(iota)

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
        for iota in parse_iota(pattern_registry, line):
            level = iota.preadjust(level)
            iota.print(level, args.highlight)
            level = iota.postadjust(level)
