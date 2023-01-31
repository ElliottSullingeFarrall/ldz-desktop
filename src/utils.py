'''Module containing additional resources for running app.
'''

from __future__ import annotations
from typing import Union

import tkinter as tk
from tkinter import font as tkf
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

DATA_DIR: str = appdirs.user_data_dir('LDZ', 'ElliottSF', roaming=True)

def resource_path(relative_path: str) -> str:
    """Converts directory path to allow access in compiled app.

    Args:
        relative_path (str): Path of resource in non-compiled app.

    Returns:
        str: Path of resource in compiled app.
    """    
    wd: str = os.getcwd()
    os.chdir(os.path.dirname(sys.argv[0]))
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path: str = sys._MEIPASS
    except Exception:
        base_path: str = os.path.abspath(".")
    os.chdir(wd)
    return os.path.join(base_path, relative_path)

# ---------------------------------------------------------------------------- #
#                                  GUI Tweaks                                  #
# ---------------------------------------------------------------------------- #

def gridx(self: tk.Widget, *args, **kwargs) -> tk.Widget:
    """Custom method for tk.Widget to allow method chaining when using grid layout.

    Returns:
        tk.Widget: Tkinter widget class.
    """    
    self.grid(*args, **kwargs)
    return self
tk.Widget.gridx: callable = gridx

def expand_dropdown(event: tk.Event):
    """Function to expand dropdown menu to accomodate longest possible option.

    Args:
        event (tk.Event): Tkinter event.
    """    
    combo: tk.Widget = event.widget
    style: ttk.Style = ttk.Style(combo.master)

    long: str = max(combo.cget('values'), key=len)

    font: tkf.Font = tkf.nametofont(str(combo.cget('font')))
    width: int = max(0, font.measure(long.strip() + '0') - combo.winfo_width())

    style.configure('TCombobox', postoffset=(0,0,width,0))
