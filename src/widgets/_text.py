from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from tkinter import ttk

from . import Widget


class Text(Widget):
    def __init__(
        self,
        profile: Profile,
        label: str = "",
        default: str = "",
        required: bool = True,
    ) -> None:
        super().__init__(
            profile, labels=(label,), defaults=(default,), required=required
        )

        self.label0 = ttk.Label(self.profile, text=f"{self.labels[0]}:")
        self.field0 = ttk.Entry(self.profile, textvariable=self.vars[0])

        self.label0.grid(row=self.row, column=0, sticky="e")
        self.field0.grid(row=self.row, column=1, sticky="ew", columnspan=3)
