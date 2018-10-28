#!/usr/bin/env python

# Converts a module to Concrete Settings class
# The current values are used to guess the setting type hint


import argparse
import importlib.util
import typing
from pathlib import Path

from concrete_settings import(
    settings_from_module, Setting, SettingsMeta
)

# ~/.virtualenvs/django1.11/lib/python3.6/site-packages/django/conf/global_settings.py

def setup_and_parse_args():
    parser = argparse.ArgumentParser(description='Convert a module to ConcreteSettings class')
    parser.add_argument('path_or_module',
                        help='a file or Python module to convert')
    return parser.parse_args()


def main():
    args = setup_and_parse_args()

    class_name: str = 'SettingsClassNameFromModuleOrFile'
    outfile: 'FileDescriptor' = None

    path = Path(args.path_or_module)
    if path.exists() and path.is_file():
        spec = importlib.util.spec_from_file_location(path.stem, path.resolve())
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        module = __import__(args.path_or_module)

    cls = settings_from_module(module, class_name=class_name)
    print(render_settings_cls(cls))


def render_settings_cls(cls):
    res = []
    res.append(f'class {cls.__name__}:')

    for attr, field in cls.__dict__.items():
        if not SettingsMeta.is_setting_name(attr):
            continue
        s = render_setting(attr, field)
        res.append(f'    {s}')
    return '\n'.join(res)


def render_setting(attr, field):
    default_val = field.value
    if isinstance(field.type_hint, typing._TypingBase):
        type_hint_obj = str(field.type_hint)
    else:
        type_hint_obj = field.type_hint.__qualname__

    if isinstance(default_val, str):
        default_val = f"\'{default_val}\'"

    return f'{attr}: {type_hint_obj} = Setting({default_val})'


if __name__ == '__main__':
    main()
