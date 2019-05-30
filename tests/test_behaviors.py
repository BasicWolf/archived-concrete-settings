import pytest

from concrete_settings import Settings, Setting, Deprecated


# == DeprecatedSetting == #


# def test_deprecated_setting_raises_warning_when_validated():
#     with pytest.warns(
#         DeprecationWarning,
#         match=r"Setting `D` in class `<class 'test_concrete_settings.test_deprecated_setting_raises_warning_when_validated.<locals>.S'>` is deprecated.",
#     ) as w:

#         class S(Settings):
#             D = DeprecatedSetting(100)

#         S().is_valid()
#         assert len(w) == 1


# def test_deprecated_setting_raises_warning_when_accessed():
#     class S(Settings):
#         D = DeprecatedSetting(100)

#     with pytest.warns(DeprecationWarning):
#         S().is_valid()

#     with pytest.warns(
#         DeprecationWarning,
#         match=r"Setting `D` in class `<class 'test_concrete_settings.test_deprecated_setting_raises_warning_when_accessed.<locals>.S'>` is deprecated",
#     ) as w:
#         x = S().D
#         assert len(w) == 1


def test_deprecated_warns_when_validating():
    class S(Settings):
        D = Setting(10) @ Deprecated()

    with pytest.warns(DeprecationWarning) as w:
        S().is_valid()