from dataclasses import dataclass, asdict
from typing import Iterable, Protocol


@dataclass
class BaseDataClass:
    def to_dict(self) -> dict[str, any]:
        return asdict(self)
    
@dataclass
class BaseParameters(Protocol):
    max_results: int
    id: Iterable[str] | str | None = None
    properties_details: Iterable[str] | str | None = None