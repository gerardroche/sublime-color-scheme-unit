import html

from sublime import Region
from sublime import set_clipboard
from sublime import status_message
import sublime_plugin

from ColorSchemeUnit.lib.color_scheme import ViewStyle
from ColorSchemeUnit.lib.generator import generate_color_scheme_assertions
from ColorSchemeUnit.lib.runner import ColorSchemeUnit
from ColorSchemeUnit.lib.runner import get_color_scheme_test_params_from_view
from ColorSchemeUnit.lib.runner import is_valid_color_scheme_test_file_name


class ColorSchemeUnitGenerateAssertions(sublime_plugin.TextCommand):

    def run(self, edit):
        point = self.view.sel()[0].begin()
        line = self.view.line(point)
        assertions = generate_color_scheme_assertions(self.view, point)
        self.view.insert(edit, line.end(), '\n' + assertions)


class ColorSchemeUnitEvents(sublime_plugin.EventListener):

    def on_load_async(self, view):
        if is_valid_color_scheme_test_file_name(view.file_name()):
            params = get_color_scheme_test_params_from_view(view)
            if params and params['syntax']:
                view.settings().set('color_scheme', params['color_scheme'])
                view.assign_syntax(params['syntax'])


class ColorSchemeUnitSetupTestFixtureCommand(sublime_plugin.TextCommand):

    def run(self, edit, content):
        self.view.erase(edit, Region(0, self.view.size()))
        self.view.insert(edit, 0, content)


class ColorSchemeUnitShowStyles(sublime_plugin.WindowCommand):

    def run(self):
        view = self.window.active_view()
        point = view.sel()[-1].b
        scope = view.scope_name(point)
        style = ViewStyle(view).at_point(point)

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
            style_html += "<li>{0}: <a href=\"{1}\">{1}</a></li>".format(x, html.escape(str(style[x])))
        style_html += '</ul>'

        html_str = """
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

        view.show_popup(
            html_str,
            max_width=512,
            max_height=700,
            on_navigate=lambda x: copy(view, x))


class ColorSchemeUnitTestSuite(sublime_plugin.WindowCommand):

    def run(self, package=None):
        ColorSchemeUnit(self.window).run(package)


class ColorSchemeUnitTestFile(sublime_plugin.WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run_file()
