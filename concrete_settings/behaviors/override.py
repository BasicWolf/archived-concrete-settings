from typing import TYPE_CHECKING

from .behavior import Behavior

if TYPE_CHECKING:
    from ..settings import Setting


class override(Behavior):
    def decorate(self, setting: 'Setting'):
        setting.override = True
        super().decorate(setting)
