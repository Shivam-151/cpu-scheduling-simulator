from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0

    remaining: int = field(init=False)
    completion: int = 0
    turnaround: int = 0
    waiting: int = 0
    response: int = -1
    first_start: Optional[int] = None

    def __post_init__(self):
        self.remaining = self.burst