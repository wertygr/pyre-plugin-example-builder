from typing import TypedDict, Any, is_typeddict, get_type_hints, get_origin, get_args


class Config(TypedDict):
    file: str
    cache: bool
    api: bool


class Meta(TypedDict):
    name: str
    title: str
    description: str
    tags: list[str]
    blacklist: list[str]
    config: Config

def is_valid(data: Any, schema: Any) -> bool:
    if is_typeddict(schema):
        if not isinstance(data, dict):
            return False
        hints = get_type_hints(schema)
        return all(
            key in data and is_valid(data[key], expected)
            for key, expected in hints.items()
        )

    if get_origin(schema) is list:
        if not isinstance(data, list):
            return False
        (item_type,) = get_args(schema)
        return all(is_valid(item, item_type) for item in data)

    if schema is int and isinstance(data, bool):
        return False
    return isinstance(data, schema)