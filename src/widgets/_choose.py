from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.profiles import Profile

from tkinter import ttk

from . import Widget


class Choose(Widget):
    def __init__(
        self,
        profile: Profile,
        label: str = "",
        default: str = "",
        values: List[str] = [""],
    ) -> None:
        super().__init__(profile, labels=(label,), defaults=(default,))
        self.values = values

        self.label0 = ttk.Label(self.profile, text=f"{self.labels[0]}:")
        self.field0 = ttk.Combobox(
            self.profile,
            textvariable=self.vars[0],
            values=self.values,
            state="readonly",
        )

        self.label0.grid(row=self.row, column=0, sticky="e")
        self.field0.grid(row=self.row, column=1, sticky="ew", columnspan=3)

        self.field0.bind("<ButtonPress>", self.expand_dropdown)
