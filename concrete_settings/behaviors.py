import functools
import types
import warnings

from .validators import DeprecatedValidator


class SettingBehavior:
    pass


class Deprecated(SettingBehavior):
    def __init__(
        self,
        deprecation_message: str = 'Setting `{name}` in class `{cls}` is deprecated.',
        validate_as_error=False,
        warn_on_get=False,
        warn_on_set=False,
    ):
        self.deprecation_message = deprecation_message
        self.validate_as_error = validate_as_error
        self.warn_on_get = warn_on_get
        self.warn_on_set = warn_on_set

    def __rmatmul__(self, st: 'concrete_settings.Setting'):
        st.validators = (
            DeprecatedValidator(self.deprecation_message, self.validate_as_error),
        ) + st.validators

        if self.warn_on_get:
            original_dget = st.__descriptor__get__

            @functools.wraps(st.__descriptor__get__)
            def wrapped_dget(me, instance, owner):
                if instance and not instance.validating:
                    msg = self.deprecation_message.format(cls=owner, name=me.name)
                    warnings.warn(msg, DeprecationWarning)
                return original_dget(instance, owner)

            st.__descriptor__get__ = types.MethodType(wrapped_dget, st)

        if self.warn_on_set:
            original_dset = st.__descriptor__set__

            @functools.wraps(st.__descriptor__set__)
            def wrapped_dset(me, instance, value):
                if not instance.validating:
                    msg = self.deprecation_message.format(
                        cls=type(instance), name=me.name
                    )
                    warnings.warn(msg, DeprecationWarning)
                original_dset(instance, value)

            st.__descriptor__set__ = types.MethodType(wrapped_dset, st)
        return st
