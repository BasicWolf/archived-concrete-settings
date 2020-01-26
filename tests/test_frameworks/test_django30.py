import logging

from concrete_settings.contrib.frameworks.django30 import Django30Settings


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
