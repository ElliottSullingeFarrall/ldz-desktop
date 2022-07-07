import PyInstaller.__main__
import os
import shutil
import platform

seps = {"Windows" : ";", "Darwin" : ":"}
icons = {"Windows" : "stag.ico", "Darwin" : "stag.icns"}

args_run = [
    "Record.py",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--distpath=",
    f"-i=images/{icons[platform.system()]}",
    f"--add-data=images/*.png{seps[platform.system()]}.",
    "--hidden-import=babel.numbers"
]
args_sync = [
    "Sync.py",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--distpath=",
    f"-i=images/{icons[platform.system()]}",
    f"--add-data=images/*.png{seps[platform.system()]}."
]

PyInstaller.__main__.run(args_run)
PyInstaller.__main__.run(args_sync)

files = ["Record.app", "Sync.app", "Record.spec", "Sync.spec", "build"]
for file in files:
    if os.path.exists(file):
        try:
            os.remove(file)
        except Exception:
            shutil.rmtree(file)
        print(f"{file} removed")
print("Done!")