from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Frame:
    metadata: Dict[str, Any]
    payloads: List[Dict[str, Any]]
    raw_json: str