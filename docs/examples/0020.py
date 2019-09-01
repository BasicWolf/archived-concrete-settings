from concrete_settings import Settings, Setting
from concrete_settings.validators import ValueTypeValidator

class AppSettings(Settings):
    DEBUG = Setting(
        True,
        type_hint=bool,
        validators=(ValueTypeValidator(), ),
        doc="Turns debug mode on/off"
    )
