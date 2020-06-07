from typing import TYPE_CHECKING

from .behavior import Behavior

if TYPE_CHECKING:
    from ..core import Setting


class override(Behavior):
    def attach_to(self, setting: 'Setting'):
        setting.override = True
        super().attach_to(setting)
        return setting
