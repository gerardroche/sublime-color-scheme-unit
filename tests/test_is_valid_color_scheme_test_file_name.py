from unittest import TestCase

from ColorSchemeUnit.lib.runner import is_valid_color_scheme_test_file_name


class TestIsValidColorSchemeTestFileName(TestCase):

    def test_valid(self):
        self.assertTrue(is_valid_color_scheme_test_file_name('color_scheme_test.txt'))
        self.assertTrue(is_valid_color_scheme_test_file_name('/path/to/color_scheme_test.txt'))
        self.assertTrue(is_valid_color_scheme_test_file_name('color_scheme_test.php'))
        self.assertTrue(is_valid_color_scheme_test_file_name('color_scheme_test.html'))
        self.assertTrue(is_valid_color_scheme_test_file_name('color_scheme_test_description.html'))
        self.assertTrue(is_valid_color_scheme_test_file_name('color_scheme_test_42.html'))

    def test_invalid(self):
        self.assertFalse(is_valid_color_scheme_test_file_name(''))
        self.assertFalse(is_valid_color_scheme_test_file_name('foobar'))
        self.assertFalse(is_valid_color_scheme_test_file_name('/path/to/foobar.txt'))
        self.assertFalse(is_valid_color_scheme_test_file_name('foobar_color_scheme_test.txt'))
        self.assertFalse(is_valid_color_scheme_test_file_name('/path/to/foobar_color_scheme_test.txt'))
        self.assertFalse(is_valid_color_scheme_test_file_name('/path/to/color_scheme_test/test.txt'))
