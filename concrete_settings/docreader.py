from sphinx.pycode.parser import Parser


def extract_docstrings(code):
    parser = Parser(code)
    parser.parse()
    pass
