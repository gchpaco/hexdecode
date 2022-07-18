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