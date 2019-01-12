from concrete_settings import (
    Settings, SettingsHistory
)

from .common import INT_VAL, FLOAT_VAL, STR_VAL, STR_CONST


def test_settings_history_smoke():
    class S0(Settings):
        DEMO: int = INT_VAL

    sh = SettingsHistory(S0)
    assert len(sh.DEMO) == 1

    assert S0 is sh.DEMO[0]


def test_settings_multiple():
    class S0(Settings):
        DEMO: int = INT_VAL

    class S1(S0):
        pass

    class S2(S1):
        DEMO = S1.DEMO + 1

    sh = SettingsHistory(S2)
    assert len(sh.DEMO) == 2
