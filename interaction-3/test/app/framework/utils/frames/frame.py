import json

class Frame:
    """
    A frame received from another device.
    """
    def __init__(self, metadata, action, value):
        self.metadata = Metadata(
            sender_id=metadata["senderId"],
            timestamp=metadata["timestamp"],
        )
        self.action = action
        self.value = value
    
    def to_json(self):
        data = {
            "metadata": {
                "senderId": self.metadata.sender_id,
                "timestamp": self.metadata.timestamp,
            },
            "action": self.action,
            "value": self.value,
        }

        return json.dumps(data)

    def __str__(self):
        return f"""

metadata: {self.metadata}
action: {self.action}
value: {self.value}
"""

class Metadata:
    """
    Frame metadata.
    """
    def __init__(self, sender_id, timestamp):
        self.sender_id = sender_id
        self.timestamp = timestamp

    def __str__(self):
        return f"""
    sender_id: {self.sender_id}
    timestamp: {self.timestamp}"""
