from __future__ import annotations
import nbtlib
import struct
from hexast import Direction, Angle, UnknownPattern, Vector, NumberConstant, Entity, Null, BooleanConstant

def _repack_vec3s(vector):
    args = [NumberConstant(struct.unpack("d", struct.pack("q", element.unpack()))[0])
            for element in vector]
    return Vector(*args)
def _parse_type(type, data):
    match type:
        case 'hexcasting:pattern':
            start_dir = Direction(data['start_dir'].unpack())
            angles = ''.join([Angle.from_number(angle.unpack()).letter for angle in data['angles']])
            return UnknownPattern(start_dir, angles)
        case 'hexcasting:list':
            return [_parse_stanza(element) for element in data]
        case 'hexcasting:null':
            return Null()
        case 'hexcasting:entity':
            return Entity(data['uuid'])
        case 'hexcasting:vec3':
            return _repack_vec3s(data)
        case 'hexcasting:double':
            return NumberConstant(data.unpack())
        case 'hexcasting:boolean':
            return BooleanConstant(data.unpack())
        case 'hexcasting:garbage':
            return Null()
        case _:
            raise RuntimeError(f"Not sure what to do with {type}, {data}")
def _parse_stanza(stanza):
    match stanza:
        case {'pattern': pattern}:
            start_dir = Direction(pattern['start_dir'].unpack())
            angles = ''.join([Angle.from_number(angle.unpack()).letter for angle in pattern['angles']])
            return UnknownPattern(start_dir, angles)
        case {'list': list}:
            return [_parse_stanza(element) for element in list]
        case {'entity': entity}:
            return Entity(entity['uuid'])
        case {'widget': "NULL"}:
            return Null()
        case {'vec3': array}:
            return _repack_vec3s(array)
        case {'double': double}:
            return NumberConstant(double.unpack())
        case {'hexcasting:type': type, 'hexcasting:data': data}:
            return _parse_type(type, data)
        case _:
            raise RuntimeError(f"Not sure what to do with {stanza}")
def _parse_spellbook(nbt):
    for page, contents in nbt['pages'].items():
        name = nbt['page_names'].get(page, "(unnamed)")
        spell = _parse_stanza(contents)
        yield name, spell
def _parse_trinket(nbt):
    name = nbt['display'].get('Name', "(unnamed)")
    spell = [_parse_stanza(pattern) for pattern in nbt['patterns']]
    yield name, spell

def parse(text):
    text = text.strip()
    if text.startswith("Item.of"): # kubejs output
        type_start = text.find("'")
        assert type_start != -1
        type_end = text.find("'", type_start+1)
        assert type_end != -1
        type = text[type_start+1:type_end]
        object_start = text.find('"')
        object_end = text.rfind('"')
        object = text[object_start+1:object_end]
        object = object.replace('\\"', '"')
        object = object.replace('\\\\', '\\')
        nbt = nbtlib.parse_nbt(object)
    else:
        whole = nbtlib.parse_nbt(text)
        type = whole['id']
        nbt = whole['tag']

    match type:
        case "hexcasting:spellbook":
            yield from _parse_spellbook(nbt)
        case "hexcasting:trinket":
            yield from _parse_trinket(nbt)
        case other:
            raise RuntimeError(f"Dunno how to handle objects like {other}")
