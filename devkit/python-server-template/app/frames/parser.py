import json
from aiohttp import web
from app.frames.frame import Frame


class FrameParser:
    frame = None

    def __init__(self, raw_frame: str):
        try:
            self.frame = self.load(raw_frame)
        except Exception as e:
            raise RuntimeError(f"FrameParser: Cannot load frame. Reason: {e}")

        try:
            self.validate()
        except Exception as e:
            raise RuntimeError(f"FrameParser: Cannot validate frame. Reason: {e}")

    def load(self, raw_frame: str):
        return json.loads(raw_frame)

    def validate(self):
        if self.frame is None:
            raise RuntimeError("FrameParser: Cannot validate frame. Reason: frame is None")

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

        if errors:
            raise RuntimeError(f"FrameParser: Cannot load frame. Errors: {errors}")

    def parse(self) -> Frame:
        return Frame(
            metadata=self.frame["metadata"],
            payloads=self.frame["payload"],
            raw_json=json.dumps(self.frame),
        )


async def parse_frame_from_request(request: web.Request) -> Frame:
    """
    Reads HTTP JSON body and validates it as a Frame.
    Accepts:
      - JSON object (normal HTTP)
      - raw string containing JSON (rare)
    """
    try:
        body = await request.json()
    except Exception:
        raw = await request.text()
        parser = FrameParser(raw)
        return parser.parse()

    # body is a dict/list -> must be dict Frame
    raw = json.dumps(body)
    parser = FrameParser(raw)
    return parser.parse()