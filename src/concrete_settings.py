from typing import Any, Callable, List, Tuple, get_type_hints,


class Undefined:
    pass


class Guess:
    pass


def validate_type(settings, new_val):
    pass



class SettingsMeta(type):
    def __new__(cls, name, bases, dct):
        base_settings = self.collect_base_settings(bases)

        cls = super().__new__(cls, name, bases, dct)
        return cls

    def collect_base_settings(self, bases):
        '''
        Iterate through class bases, lookup `Setting` descriptor-attributes
        '''
        setting_attributes = {}

        for base in bases:
            for k, v in base.__dict__.items():
                if isinstance(v, Setting):
                    # In case of multiple base classes with same settings
                    # - Mixins or multiple inheritance,
                    # check if setting has already been defined
                    # and update its history if required
                    if k in setting_attributes:
                        self.update_setting(setting_attributes[k], base, v)
                    else:
                        setting_attributes[k] = v

    def update_setting(self, setting, new_base, new_setting_or_val):
        setting.update(new_base, new_setting_or_val)



class Settings(metaclass=SettingsMeta):
    pass


class Setting:
    # TODO: slots

    override: bool
    val: Any


    def __init__(self,
                 default_val: Any = Undefined,
                 type_hint: Any = Guess,
                 description: str = '',
                 validator: Callable = validate_type,
                 sealed: bool = False):
        self.val = default_val
        self.type_hint = type_hint
        self.description = description
        self.sealed = sealed
        self.validator = validator

        self._history: List[Tuple[str, str]] = []

        self._name = ''
        self._owner_name = ''

    def __set_name__(self, owner, name):
        self._owner_name = owner.__name__
        self._name = name

    @property
    def full_name(self):
        return self.owner_name + '_' + self._name

    def update(self, new_owner, new_val):
        if isinstance(new_val, Setting):
            raise ValueError(
                f'Setting {self.name} defined in {self._owner_name} is overriden. '
                'Use OverrideSetting class to override a setting definition explicitly.'
            )
        elif isinstance(new_val, OverrideSetting):
            pass
        else:
            pass

    def __get__(self, obj, objtype):
        if self.val == Undefined:
            raise ValueError(f'Setting {self.full_name} value has not been set')

        return self.val

    def __set__(self, obj, val):
        if self.sealed:
            raise AttributeError(f'Cannot set sealed setting {self.full_name} value')

        if self.validator:
            self.validator(self, val)
        self.val = val


class OverrideSetting(Setting):
    pass
