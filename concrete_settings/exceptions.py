class SettingsError(Exception):
    pass


class SealedSettingError(SettingsError):
    def __init__(self, attr):
        super().__init__(
            f'TODO: History; Setting "{attr}" in class "[TODO]"'
            ' is sealed and cannot be changed in class "[TODO]".'
            ' HINT: Define a setting via OverrideSetting() descriptor to override'
            ' the sealed setting type and value explicitly.'
        )

class TypeHintDiffersError(SettingsError):
    def __init__(self, attr):
        super().__init__(
            f'TODO: History; Setting "{attr}" in class "[TODO]"'
            ' has a different type hint that definition in class "[TODO]".'
            ' HINT: Define a setting via OverrideSetting() descriptor to override'
            ' the existing setting type explicitly.'
        )


class DescriptionDiffersError(SettingsError):
    def __init__(self, attr):
        super().__init__(
            f'TODO: History; Setting "{attr}" in class "[TODO]"'
            ' has a different description than definition in class "[TODO]".'
            ' HINT: Define a setting via OverrideSetting() descriptor to override'
            ' the existing setting description explicitly.'
        )


class ValidatorsDiffersError(SettingsError):
    # TODO: More details, which validators differ?
    def __init__(self, attr):
        super().__init__(
            f'TODO: History; Setting "{attr}" in class "[TODO]"'
            ' has different validators than definition in class "[TODO]".'
            ' HINT: Define a setting via OverrideSetting() descriptor to override'
            ' the existing setting validators explicitly.'
        )


class AttributeShadowError(SettingsError):
    def __init__(self, attr):
        super().__init__(
            f'TODO: History; Setting in class "[TODO]" overrides an'
            ' existing attribute "{attr}" defined in class "[TODO]".'
            ' HINT: Define a setting via OverrideSetting() descriptor to override'
            ' the attribute explicitly.'
        )


class UndefinedValueError(SettingsError):
    def __init__(self, setting_name):
        super().__init__(f'Setting {setting_name} value has not been set')
