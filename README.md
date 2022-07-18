# Hex casting decoder

From an original idea by https://github.com/object-Object that has since ... metastasized.

Needs Lark and nbtlib; `pip install lark` and `pip install nbtlib` if you don't have it in whatever virtualenv this lives in.

To use, download the Java files
https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/java/at/petrak/hexcasting/common/casting/RegisterPatterns.java
https://github.com/gamma-delta/HexMod/blob/main/Fabric/src/main/java/at/petrak/hexcasting/fabric/interop/gravity/GravityApiInterop.java
https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/java/at/petrak/hexcasting/interop/pehkui/PehkuiInterop.java

Build the pattern registry with
```
$ python buildpatterns.py *.java > pattern_registry.json
```
then submit your patterns on stdin with
```
$ echo 'gobbletygook goes here' | python hexdecode.py pattern_registry.json
```

If you'd like the fanciful names rather than the internal ones, download https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/resources/assets/hexcasting/lang/en_us.json (or whatever your preferred supported language is) and give it as the second argument:
```
$ echo 'gobbletygook goes here' | python hexdecode.py pattern_registry.json en_us.json
```

A useful thing if you're on a Mac:
```
$ pbpaste | python hexdecode.py pattern_registry.json en_us.json | pbcopy
```
This takes the clipboard, decodes it, and puts the result back onto the clipboard for pasting.
