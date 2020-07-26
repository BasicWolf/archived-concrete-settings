from uuid import UUID

import pytest

from concrete_settings import ValidationError
from concrete_settings.contrib.settings.uuid import UUIDSetting, UUIDValidator


def test_uuid_string_set_as_uuid_value():
    class Parent:
        id: UUID = UUIDSetting()

    parent = Parent()
    parent.id = '77e7bb7b-6a44-4069-ba04-bc4835cb31e5'

    assert parent.id == UUID('77e7bb7b-6a44-4069-ba04-bc4835cb31e5')


def test_uuid_value_not_set_from_invalid_string():
    class Parent:
        ID: UUID = UUIDSetting()

    parent = Parent()
    parent.ID = '77e7bb7b-6a44-4069-ba04'

    assert parent.ID == '77e7bb7b-6a44-4069-ba04'


def test_uuid_validator_raises_validation_error():
    with pytest.raises(ValidationError):
        UUIDValidator()('aaa')


def test_uuid_validator_pass():
    UUIDValidator('86a63624-7442-4e0e-b880-d03a6f154705')
