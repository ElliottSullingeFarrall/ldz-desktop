import PyInstaller.__main__
import os
import shutil
import platform

args_run = [
    "Record.py",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--distpath=",
    "--add-data=images/*.png;.",
    "--hidden-import=babel.numbers",
]
args_sync = [
    "Sync.py",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--distpath=",
    "--add-data=images/*.png;.",
]

icons = {"Windows" : "stag.ico", "Darwin" : "stag.icns"}
args_run.append(f"-i=images/{icons[platform.system()]}")
args_sync.append(f"-i=images/{icons[platform.system()]}")

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