import os
import re
from typing import Any, Optional

import yaml
from pydantic import TypeAdapter

ENV_PATTERN = r'\$env\["([^"]+)"\]'


class ConfigException(Exception):
    pass


class EnvNotSetException(ConfigException):
    def __init__(self, env_var: str):
        super().__init__(f"Environment variable '{env_var}' is not set.")


def get_env_key_value(
    pattern: str, value: str, strict: bool = True
) -> tuple[bool, Optional[str], Optional[str]]:
    match = re.match(pattern, value)
    if not match:
        return (False, "", None)
    env_key = match.group(1)
    env_value = os.environ.get(env_key, "$$null")
    if strict and env_value == "$$null":
        raise EnvNotSetException(env_key)
    if not strict and env_value == "$$null":
        env_value = value
    return True, env_key, env_value


def process_yaml_data(data: Any, strict: bool = True) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("$"):
                ok, _, env_value = get_env_key_value(
                    pattern=ENV_PATTERN, value=value, strict=strict
                )
                if not ok:
                    continue
                data[key] = env_value
            elif isinstance(value, (dict, list)):
                process_yaml_data(value, strict=strict)
    elif isinstance(data, list):
        for value in data:
            process_yaml_data(value, strict=strict)


def recursive_merge(original: Any, to_merge: Any) -> Any:
    for key, value in to_merge.items():
        if key in original:
            if isinstance(original[key], dict) and isinstance(value, dict):
                original[key] = recursive_merge(original[key], value)
            else:
                original[key] = value
        else:
            original[key] = value
    return original


def loan_and_merge_from_yaml(config_dir: str, environment: str, strict: bool = True):
    all_data: Any = []
    for env in [environment]:
        file_name = os.path.join(config_dir, f"{env}.yaml")
        if not os.path.exists(file_name):
            continue
        with open(file_name, "rb") as f:
            yaml_data = yaml.safe_load(f)
        process_yaml_data(yaml_data, strict=False)
        all_data.append(yaml_data)
    if len(all_data) == 2:
        merged_data = recursive_merge(all_data[0], all_data[1])
    else:
        merged_data = all_data[0]

    process_yaml_data(merged_data, strict=strict)
    return merged_data


class ConfigMixing:
    @classmethod
    def from_yaml(cls, config_dir: str, environment: str, strict: bool = True):
        merged_data = loan_and_merge_from_yaml(
            config_dir=config_dir, environment=environment, strict=strict
        )
        ta = TypeAdapter(cls)
        return ta.validate_python(merged_data)
