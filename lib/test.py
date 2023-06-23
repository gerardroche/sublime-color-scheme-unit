import os

from sublime import packages_path
from sublime import Region
from sublime import version


class TestView():

    def __init__(self, window, test):
        self.window = window
        self.test = test
        self.name = 'color_scheme_unit_test_view'

    def setUp(self):
        if int(version()) > 3083:
            self.view = self.window.create_output_panel(self.name, unlisted=True)
        else:
            self.view = self.window.create_output_panel(self.name)

    def settings(self):
        return self.view.settings()

    def tearDown(self):
        if self.view:
            self.view.close()

    def file_name(self):
        return os.path.join(os.path.dirname(packages_path()), self.test)

    def set_content(self, content):
        self.view.run_command('color_scheme_unit_setup_test_fixture', {'content': content})

    def get_content(self):
        return self.view.substr(Region(0, self.view.size()))


class TestOutputPanel():

    def __init__(self, window):
        self.name = 'color_scheme_output'
        self.window = window
        active_view = window.active_view()

        if active_view and active_view.settings().get('color_scheme_unit.strategy') == 'view':
            for view in window.views():
                if view.name() == self.name:
                    view.close()

            self.view = window.new_file()
            self.view.set_name(self.name)
            self.view.set_scratch(True)
        else:
            self.view = window.create_output_panel(self.name)

        settings = self.view.settings()
        settings.set('result_file_regex', '^(.+):([0-9]+):([0-9]+)$')
        settings.set('word_wrap', False)
        settings.set('line_numbers', False)
        settings.set('gutter', False)
        settings.set('rulers', [])
        settings.set('scroll_past_end', False)

        if int(version()) > 3083:
            self.view.assign_syntax('Packages/' + __name__.split('.')[0] + '/res/text-ui-result.sublime-syntax')

        if active_view:
            color_scheme = active_view.settings().get('color_scheme')
            if color_scheme:
                settings.set('color_scheme', color_scheme)

        self.show()

        self.closed = False

    def write(self, text):
        self.view.run_command('append', {'characters': text, 'scroll_to_end': True})

    def writeln(self, s):
        self.write(s + "\n")

    def flush(self):
        pass

    def show(self):
        self.window.run_command("show_panel", {"panel": "output." + self.name})

    def close(self):
        self.closed = True
