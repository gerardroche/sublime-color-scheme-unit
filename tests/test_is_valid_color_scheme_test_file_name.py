from unittest import TestCase

# TODO REMOVE TMP FIX for plugin name change
try:
    from ColorSchemeUnit.plugin import is_valid_color_scheme_test_file_name as validate
except:
    from color_scheme_unit.plugin import is_valid_color_scheme_test_file_name as validate


class TestIsValidColorSchemeTestFileName(TestCase):

    def test_valid(self):
        self.assertTrue(validate('color_scheme_test.txt'))
        self.assertTrue(validate('/path/to/color_scheme_test.txt'))
        self.assertTrue(validate('color_scheme_test.php'))
        self.assertTrue(validate('color_scheme_test.html'))
        self.assertTrue(validate('color_scheme_test_description.html'))
        self.assertTrue(validate('color_scheme_test_42.html'))

    def test_invalid(self):
        self.assertFalse(validate(''))
        self.assertFalse(validate('foobar'))
        self.assertFalse(validate('/path/to/foobar.txt'))
        self.assertFalse(validate('foobar_color_scheme_test.txt'))
        self.assertFalse(validate('/path/to/foobar_color_scheme_test.txt'))
        self.assertFalse(validate('/path/to/color_scheme_test/test.txt'))
