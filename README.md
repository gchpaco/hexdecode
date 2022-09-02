# Hex casting decoder

From an original idea by [object-Object](https://github.com/object-Object) that has since ... metastasized.

## Setup
* Download the correct `hexdecode` executable for your computer from the Releases page, as well as the latest `pattern_registry_x-y-x.pickle` file.
* If you want to build your own pattern registry, also download the `buildpatterns` executable for your computer.
* Download https://github.com/gamma-delta/HexMod/blob/main/Common/src/main/resources/assets/hexcasting/lang/en_us.json (or whatever your preferred language is).
* Put all of the downloaded files in the same folder.

## Usage
* Put your hex on the stack and cast Reveal.
* Open `.minecraft/logs/latest.log`, find the Reveal output, and copy it (should look like `[HexPattern(NORTH_EAST qaq)]`).
* Open a terminal (eg. PowerShell) in the program folder and submit your hex as follows. Replace `hexdecode` with the name of the executable that you downloaded (eg. `hexdecode-Windows-AMD64.exe`), and `pattern_registry.pickle` with the name of the pattern registry file that you downloaded.
```
echo "paste your hex here" | hexdecode pattern_registry.pickle
```
* If you'd like the fanciful names rather than the internal ones, do this instead:
```
echo "paste your hex here" | hexdecode pattern_registry.pickle en_us.json
```
* To get syntax highlighting:
```
echo "paste your hex here" | hexdecode pattern_registry.pickle en_us.json --highlight
```
* Here's a useful thing if you're on a Mac. This takes the clipboard, decodes it, and puts the result back onto the clipboard for pasting:
```
pbpaste | hexdecode pattern_registry.pickle en_us.json | pbcopy
```
* You can also run hexdecode without any input to get a "watch mode", where you can repeatedly paste hexes and press enter to decode them:
```
hexdecode pattern_registry.pickle en_us.json --highlight
```

## Manual setup
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
python buildpatterns.py pattern_registry.pickle *.java
```

## Packaging for release
* Create and enter a venv, and install the requirements from `requirements.txt`. This prevents pyinstaller from adding unnecessary dependencies to the executable.
* On each OS for which you want to package executables, run the corresponding release script (eg. `release.ps1` for Windows). The resulting executables are placed in `dist/`.
* Also create a pattern registry file named `pattern_registry_x-y-x.pickle`, where `x-y-x` is the corresponding Hex Casting version.
