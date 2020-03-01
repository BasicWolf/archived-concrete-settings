from typing import Any, Dict

from sphinx.application import Sphinx


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect('builder-inited', patch_pydomain)

    return {
        'version': '0.1',
        'env_version': 1,
        'parallel_read_safe': True,
    }


def patch_pydomain(app: Sphinx):
    # Intersphinx hack - add 'class'  to 'data' type
    py_domain = app.builder.env.domains['py']
    py_domain._role2type['class'].append('data')
    py_domain.object_types['class'].roles = ('class', 'exc', 'data', 'obj')
