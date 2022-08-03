# Hex casting decoder

From an original idea by [object-Object](https://github.com/object-Object) that has since ... metastasized.

# Setup
* Install Python. Windows users: [download the installer](https://www.python.org/downloads/) and run it. Make sure you check the box that asks if you want to install pip.
* Clone this repository; or click the green Code button, click Download ZIP, and unzip it.
* Open a terminal in the repository folder and run this command to install the dependencies:
```
pip install -r requirements.txt
```
* Download the following files and place them in the repository folder:
   * https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/java/at/petrak/hexcasting/common/casting/RegisterPatterns.java
   * https://github.com/gamma-delta/HexMod/blob/main/Fabric/src/main/java/at/petrak/hexcasting/fabric/interop/gravity/GravityApiInterop.java
   * https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/java/at/petrak/hexcasting/interop/pehkui/PehkuiInterop.java
   * https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/resources/assets/hexcasting/lang/en_us.json (or whatever your preferred language is)
* Build the pattern registry:
```
python buildpatterns.py *.java > pattern_registry.json
```

# Usage
* Put your hex on the stack and cast Reveal.
* Open `.minecraft/logs/latest.log`, find the Reveal output, and copy it (should look like `[HexPattern(NORTH_EAST qaq)]`).
* Open a terminal in the repository folder and submit your hex:
```
echo "paste your hex here" | python hexdecode.py pattern_registry.json
```
* If you'd like the fanciful names rather than the internal ones, do this instead:
```
echo "paste your hex here" | python hexdecode.py pattern_registry.json en_us.json
```
* To get syntax highlighting:
```
echo "paste your hex here" | python hexdecode.py pattern_registry.json en_us.json --highlight
```
* Here's a useful thing if you're on a Mac. This takes the clipboard, decodes it, and puts the result back onto the clipboard for pasting:
```
pbpaste | python hexdecode.py pattern_registry.json en_us.json | pbcopy
```
