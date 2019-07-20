import os
import sys
from sphinx.pycode.parser import Parser


def extract_doc_comments_from_class_or_module(module_name, cls_name=None):
    # read the contents of the module which contains the settings
    # and parse it via Sphinx parser
    module_path = getattr(sys.modules[module_name], '__file__', None)
    if not module_path or not os.path.exists(module_path):
        return {}

    with open(module_path, 'r') as f:
        module_code = f.read()
    parser = Parser(module_code)
    parser.parse()
    return parser.comments


def extract_docstrings_from_code(code):
    parser = Parser(code)
    parser.parse()
