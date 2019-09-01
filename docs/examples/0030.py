from concrete_settings import Settings


class DatabaseSettings(Settings):
    HOST: str = 'localhost'
    PORT: int = 5431
    USERNAME: str = 'testuser'
    PASSWORD: str = 'testpassword'


class LoggingSettings(Settings):
    LEVEL: str = 'info'

    # TODO: validate_all()


class AppSettings(Settings):
    DATABASE = DatabaseSettings()
    LOG = LoggingSettings()


