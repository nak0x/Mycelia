import json

from src.utils.frames.frame import Frame

class FrameParser:
    frame = None

    def __init__(self, raw_frame):
        # Try to load the frame
        try:
            self.frame = self.load(raw_frame)
        except Exception as e:
            raise RuntimeError(f"FrameParser: Cannot load frame. Reason: {e}")

        # Try to validate it
        try:
            self.validate()
        except Exception as e:
            raise RuntimeError(f"FrameParser: Cannot validate frame. Reason: {e}")

        self.parse()

    def load(self, raw_frame):
        return json.loads(raw_frame)

    def validate(self):
        if self.frame is None:
            raise RuntimeError(f"FrameParser: Cannot validate frame. Reason: frame is None")

        errors = {}

        # --- frame level ---
        if "metadata" not in self.frame:
            errors["metadata"] = "Missing 'metadata' key"
        else:
            metadata = self.frame["metadata"]

            if "senderId" not in metadata:
                errors["senderId"] = "Missing 'senderId' key"
            if "timestamp" not in metadata:
                errors["timestamp"] = "Missing 'timestamp' key"
            if "messageId" not in metadata:
                errors["messageId"] = "Missing 'messageId' key"
            if "type" not in metadata:
                errors["type"] = "Missing 'type' key"
            if "receiverId" not in metadata:
                errors["receiverId"] = "Missing 'receiverId' key"
            if "status" not in metadata:
                errors["status"] = "Missing 'status' key"
            else:
                status = metadata["status"]
                if not isinstance(status, dict) or "connection" not in status:
                    errors["status.connection"] = "Missing 'status.connection' key"

        # --- payload ---
        if "payload" not in self.frame:
            errors["payload"] = "Missing 'payload' key"
        else:
            payloads = self.frame["payload"]
            if not isinstance(payloads, list):
                errors["payload"] = "'payload' must be a list"
            else:
                for i, payload in enumerate(payloads):
                    if not isinstance(payload, dict):
                        errors[f"payload[{i}]"] = "Payload item must be a dict"
                        continue

                    if "datatype" not in payload:
                        errors[f"payload[{i}].datatype"] = "Missing 'datatype' key"
                    if "value" not in payload:
                        errors[f"payload[{i}].value"] = "Missing 'value' key"
                    if "slug" not in payload:
                        errors[f"payload[{i}].slug"] = "Missing 'slug' key"

        if errors != {}:
            print(errors)
            raise RuntimeError(f"FrameParser: Cannot load frame. Errors: {errors}")

    def parse(self):
        self.frame = Frame(
            metadata=self.frame["metadata"],
            payloads=self.frame["payload"]
        )

    def __str__(self):
        return f"Frame: {self.frame}"
