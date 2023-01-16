import PyInstaller.__main__
import os
import platform

icons = {"Windows" : "stag.ico", "Darwin" : "stag.icns"}

args_record = [
    "src/source.py",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--argv-emulation",
    "--name=LDZ",
    f"-i=src/images/{icons[platform.system()]}",
    f"--add-data=src/images/stag.png{os.pathsep}images",
    f"--add-data=src/cfg{os.pathsep}cfg",
    "--hidden-import=babel.numbers"
]

if platform.system() in ['Windows', 'Darwin']:
    PyInstaller.__main__.run(args_record)
else:
    print(f'The platform: {platform.system()} is not supported!')

print("Finished Compiling!")