from dataclasses import dataclass, asdict
from typing import Iterable, Protocol, Any

@dataclass
class BaseDataClass:
    """Base dataclass with dictionary serialization.
    
    Provides type-safe to_dict() conversion.
    """
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
      
@dataclass
class BaseParameters(Protocol):
    """Protocol defining common API query parameters.
    
    All parameter classes must implement these fields.
    """
    max_results: int
    id: Iterable[str] | str | None = None
    properties_details: Iterable[str] | str | None = None