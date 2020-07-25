from uuid import UUID

from concrete_settings.contrib.settings.uuid import UUIDSetting


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
