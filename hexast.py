class Iota:
    def __init__(self, datum):
        self._datum = datum
    def color(self) -> str:
        return ""
    def lookup_spell(self, translation_table):
        key = f"hexcasting.spell.hexcasting:{str(self._datum)}"
        if key in translation_table:
            return translation_table[key]
        else:
            return str(self._datum)
    def print(self, level: int, highlight: bool, translation_table={}):
        indent = "  " * level
        datum_name = self.lookup_spell(translation_table)
        if highlight:
            print(indent + self.color() + datum_name + "\033[00m")
        else:
            print(indent + datum_name)
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

class UnknownPattern(Pattern):
    def __init__(self, initial_direction, turns):
        super().__init__(f"unknown: {initial_direction} {turns}")
    def color(self):
        return "\033[93m" # yellow

class Mask(Pattern):
    def __init__(self, mask):
        super().__init__(f"bookkeeper {mask}")

class Number(Pattern):
    def __init__(self, value):
        super().__init__(f"number {float(value):g}")

class PatternOpener(Pattern):
    def postadjust(self, level: int) -> int:
        return level + 1

class PatternCloser(Pattern):
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

class Unknown(Iota):
    def color(self):
        return "\033[91m" # light red
