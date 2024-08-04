from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.profiles import Profile

from src.options import TOPICS_ASND, TOPICS_MASA

from ._choose import Choose


class Topic1ASND(Choose):
    def __init__(self, profile: Profile) -> None:
        super().__init__(profile, label="Topic 1", values=TOPICS_ASND)


class Topic2ASND(Choose):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile, label="Topic 2", values=["N/A"] + TOPICS_ASND, default="N/A"
        )


class Topic1MASA(Choose):
    def __init__(self, profile: Profile) -> None:
        super().__init__(profile, label="Topic 1", values=TOPICS_MASA)


class Topic2MASA(Choose):
    def __init__(self, profile: Profile) -> None:
        super().__init__(
            profile, label="Topic 2", values=["N/A"] + TOPICS_MASA, default="N/A"
        )
