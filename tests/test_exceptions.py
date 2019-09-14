from concrete_settings.exceptions import SettingsValidationError


class TestValidationError:
    def test_str_detail(self):
        assert SettingsValidationError('abc').detail == 'abc'
        assert str(SettingsValidationError('abc')) == 'abc'

    def test_list_detail(self):
        assert SettingsValidationError(['a', 'b']).detail == ['a', 'b']
        assert str(SettingsValidationError(['a', 'b'])) == "a; b"

    def test_dict_detail(self):
        assert SettingsValidationError(
            {'field': 'There has been a sad error'}
        ).detail == {'field': 'There has been a sad error'}
        assert str(
            SettingsValidationError(
                {
                    'field': 'A sad error',
                    'another_field': 'A number was expected',
                }
            )
        ) == (
            "field: A sad error.\n"
            "another_field: A number was expected."
        )

    def test_dict_with_list_detail(self):
        assert str(
            SettingsValidationError(
                {
                    'field': ['A sad error', 'A shocking error'],
                    'another_field': 'A number was expected',
                }
            )
        ) == (
            "field: A sad error; A shocking error.\n"
            "another_field: A number was expected."
        )
