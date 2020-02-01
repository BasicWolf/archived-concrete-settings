import logging
from pathlib import Path

from concrete_settings.contrib.frameworks.django30 import Django30Settings
from concrete_settings.contrib.frameworks.django30_template import MyProjectSettings


def test_django30_is_valid():
    assert Django30Settings().is_valid()


def test_Django30Settings_values_correspond_to_django_global_settings(request):
    try:
        from django.conf import global_settings
    except ImportError:
        logging.getLogger().warning(
            f"Will not continue with `{request.node.name}`: "
            "Error importing django.conf.global_settings."
        )
        return

    for name in dir(global_settings):
        # skip non-setting fields
        if name.upper() != name:
            continue

        concrete_setting_value = getattr(Django30Settings, name).value
        expected_django_value = getattr(global_settings, name)
        assert concrete_setting_value == expected_django_value


def test_django30_template_py_yml_equal():
    import concrete_settings.contrib.frameworks
    frameworks_dir = Path(concrete_settings.contrib.frameworks.__file__).parent

    django30_py = MyProjectSettings()
    django30_yml = Django30Settings()

    django30_yml.update(frameworks_dir / 'django30_template.yml')

    for name, _ in django30_py.settings_attributes:
        assert getattr(django30_yml, name) == getattr(django30_py, name)
