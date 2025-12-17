import json
import time
from datetime import datetime
from ..config import SERVER_ID, ESP32_WATER_ID, SERVER_3_ID, DEFAULT_IOS_TARGET

def build_led_message(value: bool = True) -> str:
    payload = {
        "metadata": {
            "senderId": SERVER_ID,
            "timestamp": time.time(),
            "messageId": f"MSG-{datetime.now().isoformat()}-0001",
            "type": "ws-data",
            "receiverId": ESP32_WATER_ID,
            "status": {"connection": 200},
        },
        "payload": [
            {
                "datatype": "boolean",
                "value": value,
                "slug": "led",
            }
        ],
    }
    return json.dumps(payload)

def build_interaction_done_message() -> str:
    payload = {
        "metadata": {
            "senderId": SERVER_ID,
            "timestamp": time.time(),
            "messageId": f"MSG-{datetime.now().isoformat()}-0002",
            "type": "ws-data",
            "receiverId": SERVER_3_ID,
            "status": {"connection": 200},
        },
        "payload": [
            {
                "datatype": "string",
                "value": "done",
                "slug": "interaction-2",
            }
        ],
    }
    return json.dumps(payload)

def build_robot_command(command: str, value, device_id: str = DEFAULT_IOS_TARGET) -> str:
    # Determine datatype
    if isinstance(value, bool):
        datatype = "bool"
    elif isinstance(value, int):
        datatype = "int"
    elif isinstance(value, float):
        datatype = "float"
    elif isinstance(value, list):
        datatype = "iarray"
    else:
        datatype = "string"
        value = str(value)

    payload = {
        "metadata": {
            "senderId": SERVER_ID,
            "timestamp": time.time(),
            "messageId": f"MSG-{datetime.now().strftime('%Y%m%d')}-{int(time.time() * 1000) % 10000:04d}",
            "type": "ws-data",
            "receiverId": device_id,
            "status": {"connection": 200},
        },
        "payload": [
            {
                "datatype": datatype,
                "value": value,
                "slug": command,
            }
        ],
    }
    return json.dumps(payload)
