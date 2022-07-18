from enum import Enum
import struct
import uuid

class Iota:
    def __init__(self, datum):
        self._datum = datum
    def color(self) -> str:
        return ""
    def presentation_name(self):
        return str(self._datum)
    def localize(self, translation_table):
        presentation_name = self.presentation_name()
        key = f"hexcasting.spell.hexcasting:{presentation_name}"
        if key in translation_table:
            return translation_table[key]
        else:
            return presentation_name
    def print(self, level: int, highlight: bool, translation_table={}):
        indent = "  " * level
        datum_name = self.localize(translation_table)
        if highlight:
            print(indent + self.color() + datum_name + "\033[00m")
        else:
            print(indent + datum_name)
    def preadjust(self, level: int) -> int:
        return level
    def postadjust(self, level: int) -> int:
        return level

class ListOpener(Iota):
    def presentation_name(self):
        return "["
    def postadjust(self, level: int) -> int:
        return level + 1

class ListCloser(Iota):
    def presentation_name(self):
        return "]"
    def preadjust(self, level: int) -> int:
        return level - 1

class Pattern(Iota):
    def color(self):
        return "\033[93m" # yellow

class UnknownPattern(Pattern):
    def __init__(self, initial_direction, turns):
        self._initial_direction = initial_direction
        super().__init__(turns)
    def presentation_name(self):
        return f"unknown: {self._initial_direction} {self._datum}"

class Bookkeeper(Pattern):
    def presentation_name(self):
        return f"bookkeeper: {self._datum}"

class Number(Pattern):
    def presentation_name(self):
        return f"number {float(self._datum):g}"

class PatternOpener(Pattern):
    def presentation_name(self):
        return "{"
    def postadjust(self, level: int) -> int:
        return level + 1

class PatternCloser(Pattern):
    def presentation_name(self):
        return "}"
    def preadjust(self, level: int) -> int:
        return level - 1

class NumberConstant(Iota):
    def str(self):
        return self._datum
    def color(self):
        return "\033[92m" # light green

class Vector(NumberConstant):
    def __init__(self, x, y, z):
        super().__init__(f"({x._datum}, {y._datum}, {z._datum})")

class Entity(Iota):
    def __init__(self, uuid_bits):
        packed = struct.pack("iiii", *uuid_bits)
        super().__init__(uuid.UUID(bytes_le=packed))
    def color(self):
        return "\033[92m" # light green

class Null(Iota):
    def __init__(self):
        super().__init__("NULL")
    def color(self):
        return "\033[92m" # light green

class Unknown(Iota):
    def color(self):
        return "\033[91m" # light red

class Angle(Enum):
    FORWARD    = (0, "w")
    w          = (0, "w")
    RIGHT      = (1, "e")
    e          = (1, "e")
    RIGHT_BACK = (2, "d")
    d          = (2, "d")
    BACK       = (3, "s")
    LEFT_BACK  = (4, "a")
    a          = (4, "a")
    LEFT       = (5, "q")
    q          = (5, "q")

    @classmethod
    def from_number(cls, num):
        return {0: cls.FORWARD, 1: cls.RIGHT, 2: cls.RIGHT_BACK,
           3: cls.BACK, 4: cls.LEFT_BACK, 5: cls.LEFT}[num]

    def offset(self):
        return self.value[0]

    def __init__(self, ordinal, letter):
        self.ordinal = ordinal
        self.letter = letter

class Direction(Enum): # numbers increase clockwise
    NORTH_EAST = 0
    EAST       = 1
    SOUTH_EAST = 2
    SOUTH_WEST = 3
    WEST       = 4
    NORTH_WEST = 5

    def angle_from(self, other):
        return Angle.from_number((self.value - other.value) % len(Angle))

    def rotated(self, angle):
        offset = Angle[angle].offset() if type(angle) is str else angle.offset()
        return Direction((self.value + offset) % len(Direction))

def _parse_number(pattern):
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
    return Number(accumulator)

def _get_pattern_directions(starting_direction, pattern):
    directions = [starting_direction]
    for c in pattern:
        directions.append(directions[-1].rotated(c))
    return directions

def _parse_bookkeeper(starting_direction, pattern):
    if not pattern:
        return "-"
    directions = _get_pattern_directions(starting_direction, pattern)
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

def massage_raw_pattern_list(pattern, registry):
    match pattern:
        case [*subpatterns]:
            yield ListOpener("[")
            for subpattern in subpatterns:
                yield from massage_raw_pattern_list(subpattern, registry)
            yield ListCloser("]")
        case UnknownPattern():
            if name := registry.get(pattern._datum):
                match name:
                    case "open_paren":
                        yield PatternOpener("open_paren")
                    case "close_paren":
                        yield PatternCloser("close_paren")
                    case _:
                        yield Pattern(name)
            elif bk := _parse_bookkeeper(pattern._initial_direction,
                                         pattern._datum):
                yield Bookkeeper(bk)
            elif pattern._datum.startswith(("aqaa", "dedd")):
                yield _parse_number(pattern._datum)
            else:
                yield pattern
        case other:
            yield other
