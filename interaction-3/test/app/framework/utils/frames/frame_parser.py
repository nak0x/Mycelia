import json

from framework.utils.frames.frame import Frame

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

        # --- action ---
        if "action" not in self.frame:
            errors["action"] = "Missing 'action' key"
        else:
            action = self.frame["action"]
            if not isinstance(action, str):
                errors["action"] = "'action' must be a string"

        # --- value ---
        if "value" not in self.frame:
            errors["value"] = "Missing 'value' key"

        if errors != {}:
            print(errors)
            raise RuntimeError(f"FrameParser: Cannot load frame. Errors: {errors}")

    def parse(self):
        self.frame = Frame(
            metadata=self.frame["metadata"],
            action=self.frame["action"],
            value=self.frame["value"]
        )
        return self.frame

    def __str__(self):
        return f"Frame: {self.frame}"
