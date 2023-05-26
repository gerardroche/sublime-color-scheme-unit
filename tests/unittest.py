from contextlib import contextmanager
from unittest import TestCase

import sublime


class ViewTestCase(TestCase):

    def setUp(self) -> None:
        self.view = sublime.active_window().new_file()
        self.view.set_syntax_file(sublime.find_resources('PHP.sublime-syntax')[0])

    def tearDown(self) -> None:
        if self.view:
            self.view.set_scratch(True)
            self.view.close()

    def fixture(self, content):
        self.view.run_command('color_scheme_unit_setup_test_fixture', {'content': content})

    @contextmanager
    def loadColorScheme(self, color_scheme: str):
        try:
            settings = sublime.load_settings('Preferences.sublime-settings')
            original_color_scheme = settings.get('color_scheme')
            settings.set('color_scheme', color_scheme)
            sublime.save_settings('Preferences.sublime-settings')
            yield
        finally:
            settings.set('color_scheme', original_color_scheme)
            sublime.save_settings('Preferences.sublime-settings')
