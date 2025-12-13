class Frame:
    """
    A frame received from another device.
    """
    def __init__(self, metadata, payloads):
        self.metadata = Metadata(
            sender_id=metadata["senderId"],
            receiver_id=metadata["receiverId"],
            timestamp=metadata["timestamp"],
            message_id=metadata["messageId"],
            type=metadata["type"],
            status=metadata["status"],
        )
        self.payload = PayloadList(payloads)

    def __str__(self):
        return f"""

metadata: {self.metadata}
payload: {self.payload}
"""

class Metadata:
    """
    Frame metadata.
    """
    def __init__(self, sender_id, timestamp, message_id, type, receiver_id, status):
        self.sender_id = sender_id
        self.timestamp = timestamp
        self.message_id = message_id
        self.type = type
        self.receiver_id = receiver_id
        self.status = status

    def __str__(self):
        return f"""
    sender_id: {self.sender_id}
    timestamp: {self.timestamp}
    message_id: {self.message_id}
    type: {self.type}
    receiver_id: {self.receiver_id}"""


class PayloadList:
    """
    Payload list. Can be used like any other list.
    """
    def __init__(self, payloads):
        self._payloads = [
            Payload(
                datatype=payload["datatype"],
                value=payload["value"],
                slug=payload["slug"]
            ) for payload in payloads
        ]

    def __str__(self):
        str = ""
        for payload in self:
            str += f"{payload}"
        return str

    def __iter__(self):
        return iter(self._payloads)

    def __len__(self):
        return len(self._payloads)

    def __getitem__(self, index):
        return self._payloads[index]

    def append(self, payload):
        self._payloads.append(payload)

    def extend(self, payloads):
        self._payloads.extend(payloads)

class Payload:
    """
    Unique payload of a frame.
    """
    def __init__(self, datatype, value, slug):
        self.datatype = datatype
        self.value = value
        self.slug = slug

    def __str__(self):
        return f"""
    datatype: {self.datatype}
    value: {self.value}
    slug: {self.slug}"""