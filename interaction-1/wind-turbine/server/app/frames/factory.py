import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


def error_frame_json(
    sender: str,
    receiver: str,
    message: str,
    connection_status: int = 400,
    message_id: Optional[str] = None,
) -> str:
    payload = {
        "metadata": {
            "senderId": sender,
            "timestamp": time.time(),
            "messageId": message_id or f"ERR-{datetime.now().isoformat()}",
            "type": "error",
            "receiverId": receiver,
            "status": {"connection": connection_status},
        },
        "payload": [
            {"datatype": "string", "value": message, "slug": "error"}
        ],
    }
    return json.dumps(payload)


def ok_frame(
    sender: str,
    receiver: str,
    connection_status: int = 200,
    payload: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "metadata": {
            "senderId": sender,
            "timestamp": time.time(),
            "messageId": f"OK-{datetime.now().isoformat()}",
            "type": "ack",
            "receiverId": receiver,
            "status": {"connection": connection_status},
        },
        "payload": payload or [],
    }