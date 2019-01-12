from concrete_settings.contrib import DjangoSettings_111


def test_djang_111():
    ds = DjangoSettings_111()
    assert ds.DEBUG == False
