from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from ._choose import Choose


class Assessment(Choose):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile,
            label="Assessment Related",
            values=["No", "Partially", "Directly", "Project/Dissertation"],
        )
