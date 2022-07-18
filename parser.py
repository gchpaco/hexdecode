from __future__ import annotations
from lark import Lark, Tree
from lark.visitors import Transformer
from enum import Enum
import hexast
import sys

parser = Lark('''
start: iota*

iota: "[" [iota ("," iota)*] "]"                -> list
    | "(" ( NUMBER "," NUMBER "," NUMBER ) ")"  -> vector
    | "HexPattern" "(" ( DIRECTION TURNS? ) ")" -> pattern
    | UNKNOWN                                   -> unknown

TURNS: ("a"|"q"|"w"|"e"|"d")+
UNKNOWN: DIRECTION

%import common.CNAME -> DIRECTION
%import common.SIGNED_FLOAT -> NUMBER
%import common.WS
%ignore WS
''')

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


def get_pattern_directions(starting_direction: Direction, pattern: str) -> list[Direction]:
    directions = [starting_direction]
    for c in pattern:
        directions.append(directions[-1].rotated(c))
    return directions

class ToAST(Transformer):
    def __init__(self, registry):
        self._registry = registry
        super().__init__()
    def vector(self, args) -> hexast.Vector:
        return hexast.Vector(args[0], args[1], args[2])
    def list(self, iotas):
        result = []
        result.append(hexast.ListOpener("["))
        for iota in iotas:
            if isinstance(iota, list):
                result.extend(iota)
            else:
                result.append(iota)
        result.append(hexast.ListCloser("]"))
        return result
    def pattern(self, args):
        initial_direction, *maybe_turns = args
        turns = maybe_turns[0] if len(maybe_turns) > 0 else ""
        if name := self._registry.get(turns):
            match name:
                case "open_paren":
                    return hexast.PatternOpener("{")
                case "close_paren":
                    return hexast.PatternCloser("}")
                case other:
                    return hexast.Pattern(name)
        elif mask := self._parse_mask(Direction[initial_direction], turns):
            return hexast.Mask(mask)
        elif turns.startswith(("aqaa", "dedd")):
            return self._parse_number(turns)
        else:
            return hexast.UnknownPattern(initial_direction, turns)
    def UNKNOWN(self, strings):
        return hexast.Unknown(''.join(strings))
    def NUMBER(self, number):
        return hexast.NumberConstant(''.join(number))
    def TURNS(self, turns):
        return ''.join(turns)
    def start(self, iotas):
        result = []
        for iota in iotas:
            if isinstance(iota, list):
                result.extend(iota)
            else:
                result.append(iota)
        return result

    def _parse_number(self, pattern: str) -> hexast.Number:
        negate = pattern.startswith("dedd")
        accumulator = 0
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
        return hexast.Number(accumulator)
    def _parse_mask(self, starting_direction: Direction, pattern: str) -> str | None:
        if not pattern:
            return "-"
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
                mask += "-"
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


def parse(text, registry):
    tree = parser.parse(text)
    result = ToAST(registry).transform(tree)
    for child in result:
        yield child
