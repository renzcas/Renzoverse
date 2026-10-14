from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrganRequest:
    payload: dict[str, Any]
    context_tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.payload, dict):
            raise TypeError("OrganRequest.payload must be a dictionary.")
        if not isinstance(self.context_tags, list) or not all(
            isinstance(tag, str) for tag in self.context_tags
        ):
            raise TypeError("OrganRequest.context_tags must be a list of strings.")


@dataclass
class OrganResponse:
    success: bool
    data: dict[str, Any]
    error: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.success, bool):
            raise TypeError("OrganResponse.success must be a boolean.")
        if not isinstance(self.data, dict):
            raise TypeError("OrganResponse.data must be a dictionary.")
        if self.error is not None and not isinstance(self.error, str):
            raise TypeError("OrganResponse.error must be a string or None.")
        if self.success and self.error is not None:
            raise ValueError("A successful OrganResponse cannot include an error.")
        if not self.success and not self.error:
            raise ValueError("A failed OrganResponse must include an error message.")
