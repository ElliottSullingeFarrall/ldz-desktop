from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from datetime import datetime
from tkinter import ttk

from . import Widget


class Times(Widget):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile,
            labels=("In", "Out"),
            defaults=(
                f"{datetime.now():%H}",
                f"{datetime.now():%M}",
                f"{datetime.now():%H}",
                f"{datetime.now():%M}",
            ),
        )

        frame = ttk.Frame(self.profile)
        frame.grid(row=self.row, column=1, sticky="ew", columnspan=3)
        frame.grid_columnconfigure(tuple(range(6)), weight=1)

        self.labelf = ttk.Label(self.profile, text="Time ")
        self.label0 = ttk.Label(frame, text=f"{self.labels[0]}:")
        self.field0a = ttk.Spinbox(
            frame,
            textvariable=self.vars[0],
            values=[f"{hour:02}" for hour in range(0, 24, 1)],
            state="readonly",
            wrap=True,
            width=3,
        )
        self.field0b = ttk.Spinbox(
            frame,
            textvariable=self.vars[1],
            values=[f"{mint:02}" for mint in range(0, 60, 5)],
            state="readonly",
            wrap=True,
            width=3,
        )
        self.label1 = ttk.Label(frame, text=f"{self.labels[1]}:")
        self.field1a = ttk.Spinbox(
            frame,
            textvariable=self.vars[2],
            values=[f"{hour:02}" for hour in range(0, 24, 1)],
            state="readonly",
            wrap=True,
            width=3,
        )
        self.field1b = ttk.Spinbox(
            frame,
            textvariable=self.vars[3],
            values=[f"{mint:02}" for mint in range(0, 60, 5)],
            state="readonly",
            wrap=True,
            width=3,
        )

        self.labelf.grid(row=self.row, column=0, sticky="e")
        self.label0.grid(row=0, column=0)
        self.field0a.grid(row=0, column=1)
        self.field0b.grid(row=0, column=2)
        self.label1.grid(row=0, column=3)
        self.field1a.grid(row=0, column=4)
        self.field1b.grid(row=0, column=5)

    def update(self, variable: str = "", index: str = "", mode: str = "") -> None:
        self.profile.form[self.labels[0]] = (
            f'{datetime.strptime(f"{self.vars[0].get()}:{self.vars[1].get()}", "%H:%M"):%H:%M}'
        )
        self.profile.form[self.labels[1]] = (
            f'{datetime.strptime(f"{self.vars[2].get()}:{self.vars[3].get()}", "%H:%M"):%H:%M}'
        )
