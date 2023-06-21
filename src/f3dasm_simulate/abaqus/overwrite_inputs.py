from typing import List, Union

from omegaconf.dictconfig import DictConfig


def _check_empty_config_rows(config: DictConfig, parent_key: Union[List, None] = None) -> List[List]:
    if parent_key is None:
        parent_key = []

    none_keys = []  # List to store keys with None value

    for key, value in config.items():
        parent_key.append(key)

        if isinstance(value, DictConfig):
            none_keys.extend(_check_empty_config_rows(value, parent_key))

        elif value is None:
            none_keys.append(parent_key[:])  # Append a copy of parent_key to none_keys

        parent_key.pop()

    return none_keys

# none_keys = [['microstructure', 'radius_mu'], ['microstructure', 'vol_req']]


def _set_config_value(config: DictConfig, keys: List, value: int):
    if len(keys) == 1:
        config[keys[0]] = value
    else:
        _set_config_value(config[keys[0]], keys[1:], value)


def overwrite_config_with_design_parameters(config: DictConfig, design_dict: dict) -> DictConfig:
    # Row of ExperimentDataframe
    # design_dict = {'vol_req': 0.2, 'radius_mu': 0.003}

    none_keys = _check_empty_config_rows(config=config)

    for keys in none_keys:
        found_key = False
        for key in design_dict:
            if key in keys:
                _set_config_value(config, keys, design_dict[key])
                found_key = True
                break

        if not found_key:
            raise KeyError(f"Key not found in none_keys: {keys}")

    return config
