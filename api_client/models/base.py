from dataclasses import dataclass, asdict
from typing import Iterable, Protocol


@dataclass
class BaseDataClass:
    def dict(self) -> dict[str, any]:
        return asdict(self)
    
@dataclass
class BaseParameters(Protocol):
    id: Iterable[str] | str | None = None
    properties_details: Iterable[str] | str | None = None
    max_results: int = 5