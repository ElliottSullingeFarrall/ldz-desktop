from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from datetime import datetime
from tkinter import ttk

import tkcalendar as tkc  # type: ignore[import-untyped]

from . import Widget


class Date(Widget):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile, labels=("Date",), defaults=(f"{datetime.now():%d/%m/%Y}",)
        )

        self.label0 = ttk.Label(self.profile, text=f"{self.labels[0]}:")
        self.field0 = tkc.DateEntry(
            self.profile,
            textvariable=self.vars[0],
            date_pattern="dd/mm/yyyy",
            selectmode="day",
            state="readonly",
        )

        self.label0.grid(row=self.row, column=0, sticky="e")
        self.field0.grid(row=self.row, column=1, sticky="ew", columnspan=3)
