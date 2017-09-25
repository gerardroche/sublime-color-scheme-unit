from sublime import Region
from sublime import set_clipboard
from sublime import status_message
from sublime_plugin import EventListener
from sublime_plugin import TextCommand
from sublime_plugin import WindowCommand

from .lib.color_scheme import ColorSchemeStyle
from .lib.generator import generate_color_scheme_assertions
from .lib.generator import generate_syntax_assertions
from .lib.runner import ColorSchemeUnit
from .lib.runner import get_color_scheme_test_params_color_scheme
from .lib.test import is_valid_color_scheme_test_file_name


class ColorSchemeUnitInsertAssertions(TextCommand):

    def run(self, edit):
        pt = self.view.sel()[0].begin()
        line = self.view.line(pt)

        self.view.insert(edit, line.end(), '\n' + generate_color_scheme_assertions(self.view, pt))


# TODO Should this helper be in its own package because it's useful for syntax devs?
class ColorSchemeUnitInsertSyntaxAssertions(TextCommand):

    def run(self, edit):
        pt = self.view.sel()[0].begin()
        line = self.view.line(pt)

        self.view.insert(edit, line.end(), '\n' + generate_syntax_assertions(self.view, pt))


class ColorSchemeUnitSetColorSchemeOnLoadEvent(EventListener):

    def on_load_async(self, view):
        if is_valid_color_scheme_test_file_name(view.file_name()):
            color_scheme = get_color_scheme_test_params_color_scheme(view)
            if color_scheme:
                view.settings().set('color_scheme', color_scheme)


class ColorSchemeUnitSetupTestFixtureCommand(TextCommand):

    def run(self, edit, content):
        self.view.erase(edit, Region(0, self.view.size()))
        self.view.insert(edit, 0, content)


class ColorSchemeUnitShowScopeNameAndStylesCommand(TextCommand):

    def run(self, edit):
        scope = self.view.scope_name(self.view.sel()[-1].b)
        style = ColorSchemeStyle(self.view).at_point(self.view.sel()[-1].b)

        style_html = '<ul>'
        if 'foreground' in style:
            style_html += "<li>foreground: <a href=\"{0}\">{0}</a></li>".format(style['foreground'].strip('#'))
            del style['foreground']
        if 'background' in style:
            style_html += "<li>background: <a href=\"{0}\">{0}</a></li>".format(style['background'].strip('#'))
            del style['background']
        if 'fontStyle' in style:
            style_html += "<li>fontStyle: <a href=\"{0}\">{0}</a></li>".format(style['fontStyle'].strip('#'))
            del style['fontStyle']
        for x in sorted(style):
            style_html += "<li>{0}: <a href=\"{1}\">{1}</a></li>".format(x, style[x])
        style_html += '</ul>'

        html = """
            <body id=show-scope>
                <style>
                    p {
                        margin-top: 0;
                    }
                    a {
                        font-family: system;
                        font-size: 1.05rem;
                    }
                    ul {
                        padding: 0;
                    }
                </style>
                <p>%s</p>
                <a href="%s">Copy</a>
                %s
            </body>
        """ % (scope.replace(' ', '<br>'), scope.rstrip(), style_html)

        def copy(view, text):
            set_clipboard(text)
            view.hide_popup()
            status_message('Scope name copied to clipboard')

        self.view.show_popup(html, max_width=512, max_height=700, on_navigate=lambda x: copy(self.view, x))


class ColorSchemeUnitTestSuiteCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run()


class ColorSchemeUnitTestFileCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run_file()


class ColorSchemeUnitTestResultsCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).results()


class ColorSchemeUnitUnitTestingCommand(WindowCommand):
    def run(self, *args, **kwargs):
        output = kwargs.get('output')
        stream = open(output, "w")

        ColorSchemeUnit(self.window).run(output=stream)
