from cx_Freeze import setup, Executable
import sys
sys.argv.append("build")

build_exe_options = {"packages": [], "excludes": None}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name = "Record" ,
    version = "" ,
    description = "" ,
    options = {"build_exe": build_exe_options},
    executables = [Executable("Record.py", base=base)])