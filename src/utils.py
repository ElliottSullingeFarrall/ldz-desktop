from __future__ import annotations
from typing import Union

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import tkcalendar as tkc

from datetime import datetime
import pandas as pd

import os
import sys
import appdirs

# ---------------------------------------------------------------------------- #
#                                  File Paths                                  #
# ---------------------------------------------------------------------------- #

DATA_DIR = appdirs.user_data_dir('LDZ', 'ElliottSF', roaming=True)

def resource_path(relative_path: str) -> str:
    wd = os.getcwd()
    os.chdir(os.path.dirname(sys.argv[0]))
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    os.chdir(wd)
    return os.path.join(base_path, relative_path)

# ---------------------------------------------------------------------------- #
#                                  GUI Tweaks                                  #
# ---------------------------------------------------------------------------- #

def gridx(self: tk.Widget, *args, **kwargs) -> tk.Widget:
    self.grid(*args, **kwargs)
    return self
tk.Widget.gridx = gridx

def gridx_rowconfigure(self: tk.Widget, *args, **kwargs) -> tk.Widget:
    self.grid_rowconfigure(*args, **kwargs)
    return self
tk.Widget.gridx_rowconfigure = gridx_rowconfigure

def gridx_columnconfigure(self: tk.Widget, *args, **kwargs) -> tk.Widget:
    self.grid_columnconfigure(*args, **kwargs)
    return self
tk.Widget.gridx_columnconfigure = gridx_columnconfigure

def expand_dropdown(event):
    combo = event.widget
    style = ttk.Style(combo.master)

    long = max(combo.cget('values'), key=len)

    font = tk.font.nametofont(str(combo.cget('font')))
    width = max(0, font.measure(long.strip() + '0') - combo.winfo_width())

    style.configure('TCombobox', postoffset=(0,0,width,0))
