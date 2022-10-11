import PyInstaller.__main__
import os
import platform

icons = {"Windows" : "stag.ico", "Darwin" : "stag.icns"}

args_record = [
    "src/Record.py",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--argv-emulation",
    f"-i=src/images/{icons[platform.system()]}",
    f"--add-data=src/images/stag.png{os.pathsep}images",
    "--hidden-import=babel.numbers"
]
args_sync = [
    "src/Sync.py",
    "--onefile",
    "--noconfirm",
    "--argv-emulation",
    f"-i=src/images/{icons[platform.system()]}",
]

if platform.system() == 'Windows':
    PyInstaller.__main__.run(args_record)
    PyInstaller.__main__.run(args_sync)
elif platform.system() == 'Darwin':
    PyInstaller.__main__.run(args_record)
else:
    print(f'The platform: {platform.system()} is not supported!')

print("Finished Compiling!")