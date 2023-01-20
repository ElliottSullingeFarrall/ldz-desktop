import os
import sys

def resource_path(relative_path):
    wd = os.getcwd()
    os.chdir(os.path.dirname(sys.argv[0]))
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    os.chdir(wd)
    return os.path.join(base_path, relative_path)

import tkinter as tk

def gridx(self, *args, **kwargs):
    self.grid(*args, **kwargs)
    return self
tk.Widget.gridx = gridx