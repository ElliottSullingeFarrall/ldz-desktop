from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from src.options import DEPARTMENTS

from ._choose import Choose


class Department(Choose):
    def __init__(self, profile: Profile) -> None:
        super().__init__(profile, label="Department", values=DEPARTMENTS)
