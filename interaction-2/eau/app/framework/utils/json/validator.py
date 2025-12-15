import json
from framework.utils.json.template import Template


class JsonValidator:
    def __init__(self, template: Template):
        self.template = template

    def validate(self, raw_data: str):
        try:
            data = json.loads(raw_data)
            return self.template.validate(data)
        except Exception as e:
            raise ValueError(f"Cannot validate json against template {self.template.name}: {e}")