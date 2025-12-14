import json
from framework.utils.json.types import JsonTypes


class TemplateBuildField:
    def __init__(self, name, value_type, required=True, default=None, children=None):
        self.name = name
        self.type = value_type
        self.required = required
        self.default = default
        self.children = children

class ConcreteTemplateField:
    def __init__(self, value_type, required=True, default=None, children=None):
        self.has_children = True
        if children is None:
            self.has_children = False
        self.type = value_type
        self.required = required
        self.default = default
        self.children = children

    def __str__(self):
        return f"Type:{self.type}, Requ:{self.required}, Def:{self.default}, Child:{self.children}"


class TemplateBuilder:

    def __init__(self):
        self.fields = []

    def build(self, name: str):
        template = Template()
        template.name = name
        for field in self.fields:
            template.add_field(field.name, ConcreteTemplateField(
                field.type,
                field.required,
                field.default,
                field.children
            ))
        return template

    def build_from_file(self, name, filepath: str):
        json_template = json.load(open(filepath))

        self.fields.extend([
            self.parse_field(field_name, value)
            for field_name, value in json_template.items()
        ])
        return self.build(name)

    def parse_field(self, name, value):
        children = {}
        if "children" in value and value["children"] is not None:
            for child_name, child_value in value["children"].items():
                children[child_name] = self.parse_field(child_name, child_value)
        return TemplateBuildField(
            name,
            value["type"],
            value.get("required", True),
            value.get("default", None),
            children
        )



class Template:
    name = ""
    _fields = {}

    def __str__(self):
        return f"Template: {self.name}"

    def add_field(self, name, value: ConcreteTemplateField):
        self._fields[name] = value

    def validate(self, data: dict, root=None, items=None):
        errors = []
        if items is None:
            items = self._fields.items()
        for field_name, template_field in items:

            # Field is not required and not present. abort.
            if not template_field.required and field_name not in data:
                continue

            # Field is not found in data dict
            if field_name not in data:
                errors.append(f"Cannot validate json: {field_name} is missing.")

            # Field is a parent - validate children
            if isinstance(data[field_name], dict):
                errors.extend(self.validate(data[field_name], field_name, template_field.children.items()))

            if not isinstance(data[field_name], JsonTypes.get_type(template_field.type)):
                errors.append(f"Cannot validate json: {field_name}: type does not match.")

        return errors