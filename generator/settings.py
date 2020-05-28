import os
from types import SimpleNamespace

import yaml


def get_settings():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'config.yml'), 'r') as config, \
            open(os.path.join(current_dir, 'default.yml'), 'r') as default:
        settings_dict = yaml.load(config, Loader=yaml.FullLoader)
        default_dict = yaml.load(default, Loader=yaml.FullLoader)
    for section_name, section in settings_dict.items():
        for item_name, item in section.items():
            if item is None:
                settings_dict[section_name][item_name] = default_dict[section_name][item_name]
        settings_dict[section_name] = SimpleNamespace(**settings_dict[section_name])
    print(settings_dict)
    return SimpleNamespace(**settings_dict)
