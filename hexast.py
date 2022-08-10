from __future__ import annotations
from enum import Enum
from itertools import pairwise
import re
import struct
from typing import Iterable
import uuid
from sty import fg
from dataclasses import dataclass, field
from math import inf

localize_regex = re.compile(r"((?:number|mask))(: .+)")

@dataclass
class PatternRegistry:
    spells: dict[str, str] = field(default_factory=dict)
    great_spells: dict[frozenset[Coord], str] = field(default_factory=dict)

class Iota:
    def __init__(self, datum):
        self._datum = datum
    def color(self) -> str:
        return ""
    def presentation_name(self):
        return str(self._datum)
    def localize(self, translation_table):
        presentation_name = self.presentation_name()
        value = ""
        if match := localize_regex.match(presentation_name):
            (presentation_name, value) = match.groups()
        key = f"hexcasting.spell.hexcasting:{presentation_name}"
        if key in translation_table:
            return translation_table[key] + value
        else:
            return presentation_name + value
    def print(self, level: int, highlight: bool, translation_table={}):
        indent = "  " * level
        datum_name = self.localize(translation_table)
        if highlight:
            print(indent + self.color() + datum_name + fg.rs)
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
        return fg.yellow

class Unknown(Iota):
    def color(self):
        return fg(124) # red

class UnknownPattern(Unknown):
    def __init__(self, initial_direction, turns):
        self._initial_direction = initial_direction
        super().__init__(turns)
    def presentation_name(self):
        return f"unknown: {self._initial_direction.name} {self._datum}"

class Bookkeeper(Pattern):
    def presentation_name(self):
        return f"mask: {self._datum}"

class Number(Pattern):
    def presentation_name(self):
        return f"number: {float(self._datum):g}"

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
        return fg.li_green

class Vector(NumberConstant):
    def __init__(self, x, y, z):
        super().__init__(f"({x._datum}, {y._datum}, {z._datum})")
    def color(self):
        return fg(207) # pink

class Entity(Iota):
    def __init__(self, uuid_bits):
        packed = struct.pack("iiii", *uuid_bits)
        super().__init__(uuid.UUID(bytes_le=packed))
    def color(self):
        return fg.li_blue

class Null(Iota):
    def __init__(self):
        super().__init__("NULL")
    def color(self):
        return fg.magenta

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


# Uses axial coordinates as per https://www.redblobgames.com/grids/hexagons/ (same system as Hex)
class Coord:
    @classmethod
    def origin(cls) -> Coord:
        return Coord(0, 0)

    def __init__(self, q: float, r: float) -> None:
        self._q = q
        self._r = r
    
    @property
    def q(self):
        return self._q
    
    @property
    def r(self):
        return self._r

    @property
    def s(self):
        # Hex has this as q - r, but the rotation formulas from the above link don't seem to work with that
        return -self.q - self.r
    
    def __hash__(self) -> int:
        return hash((self.q, self.r))
    
    def __eq__(self, other: Coord) -> bool:
        return (self.q, self.r) == (other.q, other.r)
    
    def __repr__(self) -> str:
        return f"({self.q}, {self.r})"
    
    def __add__(self, other: Direction | Coord) -> Coord:
        return self.shifted(other)
    
    def __sub__(self, other: Coord) -> Coord:
        return self.delta(other)
    
    def shifted(self, other: Direction | Coord) -> Coord:
        if isinstance(other, Direction):
            other = other.as_delta()
        return Coord(self.q + other.q, self.r + other.r)
    
    # rotates 60⁰ clockwise about the origin for each n
    def rotated_cw(self, n=1) -> Coord:
        rotated = self
        for _ in range(n):
            rotated = Coord(-rotated.r, -rotated.s)
        return rotated
    
    # rotates 60⁰ counterclockwise about the origin for each n
    def rotated_ccw(self, n=1) -> Coord:
        rotated = self
        for _ in range(n):
            rotated = Coord(-rotated.s, -rotated.q)
        return rotated
    
    def midpoint(self, other: Coord) -> Coord:
        return Coord((self.q + other.q) / 2, (self.r + other.r) / 2)
    
    def delta(self, other: Coord) -> Coord:
        return Coord(self.q - other.q, self.r - other.r)
    
    def immediate_delta(self, other: Coord) -> Direction | None:
        match other.delta(self):
            case Coord(q=1, r=0):
                return Direction.EAST
            case Coord(q=0, r=1):
                return Direction.SOUTH_EAST
            case Coord(q=-1, r=1):
                return Direction.SOUTH_WEST
            case Coord(q=-1, r=0):
                return Direction.WEST
            case Coord(q=0, r=-1):
                return Direction.NORTH_WEST
            case Coord(q=1, r=-1):
                return Direction.NORTH_EAST
            case _:
                return None

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
    
    def __mul__(self, angle: Angle) -> Direction:
        return self.rotated(angle)
    
    def as_delta(self) -> Coord:
        match self:
            case Direction.NORTH_EAST:
                return Coord(1, -1)
            case Direction.EAST:
                return Coord(1, 0)
            case Direction.SOUTH_EAST:
                return Coord(0, 1)
            case Direction.SOUTH_WEST:
                return Coord(-1, 1)
            case Direction.WEST:
                return Coord(-1, 0)
            case Direction.NORTH_WEST:
                return Coord(0, -1)

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

def _get_points(direction: Direction, pattern: str) -> tuple[Coord]:
    compass = direction
    cursor = compass.as_delta()

    points = [Coord.origin(), cursor]

    for c in pattern:
        compass = compass.rotated(Angle[c])
        cursor += compass
        points.append(cursor)

    return tuple(points)

def _centre_points_at_origin(points: Iterable[Coord]) -> frozenset[Coord]:
    min_q, max_q = inf, -inf
    min_r, max_r = inf, -inf
    for point in points:
        min_q, max_q = min(point.q, min_q), max(point.q, max_q)
        min_r, max_r = min(point.r, min_r), max(point.r, max_r)

    middle = Coord((min_q + max_q) / 2, (min_r + max_r) / 2)
    delta = Coord.origin() - middle
    return frozenset([p + delta for p in points])

def _get_line_midpoints(direction: Direction, pattern: str, centre=True) -> frozenset[Coord]:
    points = _get_points(direction, pattern)
    midpoints = [a.midpoint(b) for a, b in pairwise(points)]
    if centre:
        return _centre_points_at_origin(midpoints)
    return frozenset(midpoints)

def get_rotated_line_midpoints(direction: Direction, pattern: str):
    midpoints = _get_line_midpoints(direction, pattern, False)
    for n in range(6):
        yield _centre_points_at_origin([p.rotated_cw(n) for p in midpoints])

def _handle_named_pattern(name: str):
    match name:
        case "open_paren":
            return PatternOpener("open_paren")
        case "close_paren":
            return PatternCloser("close_paren")
        case _:
            return Pattern(name)

def massage_raw_pattern_list(pattern, registry: PatternRegistry):
    match pattern:
        case [*subpatterns]:
            yield ListOpener("[")
            for subpattern in subpatterns:
                yield from massage_raw_pattern_list(subpattern, registry)
            yield ListCloser("]")
        case UnknownPattern():
            if name := registry.spells.get(pattern._datum):
                yield _handle_named_pattern(name)
            elif bk := _parse_bookkeeper(pattern._initial_direction,
                                         pattern._datum):
                yield Bookkeeper(bk)
            elif pattern._datum.startswith(("aqaa", "dedd")):
                yield _parse_number(pattern._datum)
            else:
                midpoints = _get_line_midpoints(pattern._initial_direction, pattern._datum)
                if name := registry.great_spells.get(midpoints):
                    yield _handle_named_pattern(name)
                else:
                    yield pattern
        case other:
            yield other
