import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

def frame(
    sender: str,
    action: str,
    value: Any,
) -> Dict[str, Any]:
    return {
        "metadata": {
            "timestamp": time.time(),
            "senderId": sender,
        },
        "action": action,
        "value": value,
    }