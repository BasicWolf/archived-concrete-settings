from typing import TYPE_CHECKING, Tuple

from .behavior import Behavior

if TYPE_CHECKING:
    from ..core import Setting
    from ..validators import Validator


class validate(Behavior):
    def __init__(self, *validators: Validator):
        self._validators: Tuple[Validator, ...] = validators

    def decorate(self, setting: Setting):
        setting.validators += self._validators
        super().decorate(setting)
