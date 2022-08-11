import re
import pickle
import sys
import glob
from hexast import Direction, get_rotated_pattern_segments, PatternRegistry

# working as of https://github.com/gamma-delta/HexMod/blob/c00815b7b9d90593dc33e3a7539ce87c2ece4fc9/Common/src/main/java/at/petrak/hexcasting/common/casting/RegisterPatterns.java
# - go to https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/java/at/petrak/hexcasting/common/casting/RegisterPatterns.java
# - right click the "Raw" button, click "Save Link As", and save it with the name "RegisterPatterns.java" to the same folder as this script
#   - note: you'll have to do this again after each update, if new patterns are added or old patterns are changed

output_file = sys.argv[1]
registry_regex = re.compile(r"PatternRegistry\s*\.\s*mapPattern\s*\(\s*HexPattern\s*\.\s*fromAngles\s*\(\s*\"([aqwed]+)\"\s*,\s*HexDir\s*\.\s*(\w+)\s*\)\s*,\s*modLoc\s*\(\s*\"([\w/]+)\"\s*\).+?(true)?\);", re.M | re.S)

# parse the pattern definitions
registry = PatternRegistry()
for path in sys.argv[2:]:
    for filename in glob.glob(path):
        with open(filename, "r", encoding="utf-8") as file:
            for match in registry_regex.finditer(file.read()):
                (pattern, direction, name, is_great) = match.groups()
                if is_great:
                    for segments in get_rotated_pattern_segments(Direction[direction], pattern):
                        registry.great_spells[segments] = name
                else:
                    registry.spells[pattern] = name

with open(output_file, "wb") as file:
    pickle.dump(registry, file)

print(f"Successfully wrote pattern registry to {output_file}")
