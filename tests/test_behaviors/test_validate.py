from concrete_settings import Settings, validate


def test_validate_calls_validator(ValidatorMock):
    validator_1 = ValidatorMock()

    class AppSettings(Settings):
        AGE: int = 10 @ validate(validator_1)

    AppSettings().is_valid()
    assert validator_1.called_with_value == 10


def test_validate_calls_validators(ValidatorMock):
    validator_1 = ValidatorMock()
    validator_2 = ValidatorMock()

    class AppSettings(Settings):
        AGE: int = 10 @ validate(validator_1, validator_2)

    AppSettings().is_valid()
    assert validator_1.called_with_value == 10
    assert validator_2.called_with_value == 10
