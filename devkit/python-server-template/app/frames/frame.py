from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Frame:
    metadata: Dict[str, Any]
    action: str
    value: Optional[Any]
    raw_json: str

    @property
    def sender_id(self) -> str:
        return str(self.metadata.get("senderId", "UNKNOWN"))

    @property
    def timestamp(self) -> float:
        return float(self.metadata.get("timestamp", 0))