from concrete_settings import Settings

class AppSettings(Settings):

    #: Turns debug mode on/off
    DEBUG: bool = True

app_settings = AppSettings()
app_settings.is_valid(raise_exception=True)
print(app_settings.DEBUG)
