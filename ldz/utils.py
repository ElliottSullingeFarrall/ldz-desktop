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

import openpyxl

import os
import sys
import platformdirs
from importlib.resources import files

FROZEN: bool = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# ---------------------------------------------------------------------------- #
#                                  File Paths                                  #
# ---------------------------------------------------------------------------- #

DATA_DIR: str = platformdirs.user_data_dir('LDZ', 'ElliottSF', roaming=True)

def resource_path(relative_path: str) -> str:
    """Converts directory path to allow access in compiled app.

    Args:
        relative_path (str): Path of resource in non-compiled app.

    Returns:
        str: Path of resource in compiled app.
    """    
    if FROZEN:
        base_path: str = sys._MEIPASS
    else:
        base_path: str = files("ldz")
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
tk.Widget.gridx = gridx

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
