import json
from aiohttp import web
from app.frames.frame import Frame


class FrameParser:
    def __init__(self, raw_frame: str):
        try:
            self.frame = json.loads(raw_frame)
        except Exception as e:
            raise RuntimeError(f"FrameParser: Cannot load JSON. Reason: {e}")

        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.frame, dict):
            raise RuntimeError("FrameParser: Root must be a JSON object")

        errors = {}

        # metadata
        md = self.frame.get("metadata")
        if not isinstance(md, dict):
            errors["metadata"] = "Missing or invalid 'metadata' object"
        else:
            if "timestamp" not in md:
                errors["metadata.timestamp"] = "Missing 'timestamp'"
            if "senderId" not in md:
                errors["metadata.senderId"] = "Missing 'senderId'"

        # action
        action = self.frame.get("action")
        if not isinstance(action, str) or not action.strip():
            errors["action"] = "Missing or invalid 'action' (must be non-empty string)"

        # value is optional: can be null, primitive, object, etc.
        # no strict validation here

        if errors:
            raise RuntimeError(f"FrameParser: Validation errors: {errors}")

    def parse(self) -> Frame:
        return Frame(
            metadata=self.frame["metadata"],
            action=self.frame["action"],
            value=self.frame.get("value", None),
            raw_json=json.dumps(self.frame, ensure_ascii=False),
        )


async def parse_frame_from_request(request: web.Request) -> Frame:
    """
    Reads HTTP JSON body and validates it as the new Frame format.
    """
    try:
        body = await request.json()
        raw = json.dumps(body, ensure_ascii=False)
    except Exception:
        raw = await request.text()

    parser = FrameParser(raw)
    return parser.parse()