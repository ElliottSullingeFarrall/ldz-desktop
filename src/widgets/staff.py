from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from tkinter import ttk

from . import Widget


class Staff(Widget):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile,
            labels=("LDA", "LDL", "MASA", "FY", "Acad"),
            defaults=("No", "No", "No", "No", "No"),
        )

        frame = ttk.Frame(self.profile)
        frame.grid(row=self.row, column=1, sticky="ew", columnspan=3)
        frame.grid_columnconfigure(tuple(range(5)), weight=1)

        self.labelf = ttk.Label(self.profile, text="Staff ")
        self.label0 = ttk.Label(frame, text=f"{self.labels[0]}:", anchor="center")
        self.field0 = ttk.Checkbutton(
            frame, variable=self.vars[0], offvalue="No", onvalue="Yes"
        )
        self.label1 = ttk.Label(frame, text=f"{self.labels[1]}:", anchor="center")
        self.field1 = ttk.Checkbutton(
            frame, variable=self.vars[1], offvalue="No", onvalue="Yes"
        )
        self.label2 = ttk.Label(frame, text=f"{self.labels[2]}:", anchor="center")
        self.field2 = ttk.Checkbutton(
            frame, variable=self.vars[2], offvalue="No", onvalue="Yes"
        )
        self.label3 = ttk.Label(frame, text=f"{self.labels[3]}:", anchor="center")
        self.field3 = ttk.Checkbutton(
            frame, variable=self.vars[3], offvalue="No", onvalue="Yes"
        )
        self.label4 = ttk.Label(frame, text=f"{self.labels[4]}:", anchor="center")
        self.field4 = ttk.Checkbutton(
            frame, variable=self.vars[4], offvalue="No", onvalue="Yes"
        )

        self.labelf.grid(row=self.row, column=0, sticky="e")
        self.label0.grid(row=0, column=0, sticky="ew")
        self.field0.grid(row=1, column=0)
        self.label1.grid(row=0, column=1, sticky="ew")
        self.field1.grid(row=1, column=1)
        self.label2.grid(row=0, column=2, sticky="ew")
        self.field2.grid(row=1, column=2)
        self.label3.grid(row=0, column=3, sticky="ew")
        self.field3.grid(row=1, column=3)
        self.label4.grid(row=0, column=4, sticky="ew")
        self.field4.grid(row=1, column=4)
