from concrete_settings.exceptions import ValidationError


class TestValidationError:
    def test_str_detail(self):
        assert ValidationError('abc').detail == 'abc'
        assert str(ValidationError('abc')) == 'abc'

    def test_list_detail(self):
        assert ValidationError(['a', 'b']).detail == ['a', 'b']
        assert str(ValidationError(['a', 'b'])) == "a; b"

    def test_dict_detail(self):
        assert ValidationError(
            {'field': 'There has been a sad error'}
        ).detail == {'field': 'There has been a sad error'}
        assert str(
            ValidationError(
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
            ValidationError(
                {
                    'field': ['A sad error', 'A shocking error'],
                    'another_field': 'A number was expected',
                }
            )
        ) == (
            "field: A sad error; A shocking error.\n"
            "another_field: A number was expected."
        )
