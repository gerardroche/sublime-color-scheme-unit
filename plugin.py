from threading import Thread
import unittest
import sublime
import sublime_plugin
import os
import re
import plistlib

VERSION = '0.1.0';

DEBUG_MODE=bool(os.getenv('SUBLIME_COLOR_SCHEME_UNIT'))
DEV_TOOLS=bool(os.getenv('SUBLIME_COLOR_SCHEME_UNIT_DEV_TOOLS'))

if DEBUG_MODE:
    def debug_message(message):
        print('DEBUG [ColorSchemeUnit] %s' % str(message))
else:
    def debug_message(message):
        pass

class ColorSchemeTest(object):

    def __init__(self, test):

        self.file = os.path.join(os.path.dirname(sublime.packages_path()), test)
        self.test = test
        self.content = sublime.load_resource(test)

        if not self.content:
            raise RuntimeError('Invalid color test: no content')

        m = re.match('^COLOR TEST "(?P<color>[^"]+)" "(?P<syntax>[^"]+)"\n', self.content)

        if not m:
            raise RuntimeError('Invalid color test: no color')

        self.color = m.group('color')

        syntaxes_found = sublime.find_resources(m.group('syntax') + '.sublime-syntax')
        if len(syntaxes_found) > 1:
            raise RuntimeError('Invalid syntax: found more than one')
        if len(syntaxes_found) is not 1:
            raise RuntimeError('Invalid syntax: not found')

        self.syntax = syntaxes_found[0]
        self.content = self.content.replace('COLOR TEST "%s"\nSYNTAX TEST "%s"\n' % (self.color, self.syntax), '')

        self.assertions = []

        consecutive_test_lines = 0

        for line_number, line in enumerate(self.content.split('\n')):
            m = re.match('^//\s*(?P<repeat>\^+)(?: fg=(?P<fg>[^ ]+)?)?(?: bg=(?P<bg>[^ ]+)?)?(?: fs=(?P<fs>[^=]*)?)?$', line.lower())

            if not m:
                consecutive_test_lines = 0
            else:
                consecutive_test_lines += 1

                style = {}

                if m.group('fg') is not None:
                    style['foreground'] = m.group('fg')

                if m.group('bg') is not None:
                    style['background'] = m.group('bg')

                if m.group('fs') is not None:
                    style['fontStyle'] = m.group('fs')

                assertion = m.group(0)
                row = line_number - consecutive_test_lines
                begin = line.find('^')
                count = len(m.group('repeat'))
                end = begin + count

                self.assertions.append({
                    'style': style,
                    'count': count,
                    'row': row,
                    'begin': begin,
                    'end': end,
                    'assertion': assertion
                })

    def run(self):

        output = OutputView()

        assertion_count = 0
        failures = []

        test_view = TestView()
        test_view.setUp()

        try:
            test_view.assign_color(self.color)
            test_view.assign_syntax(self.syntax)
            test_view.set_content(self.content)

            style_util = Style(test_view.view)

            for assertion in self.assertions:

                for col in range(assertion['begin'], assertion['end']):

                    style = style_util.at_point(
                        test_view.view.text_point(
                            assertion['row'],
                            col
                        )
                    )

                    actual = {}

                    for style_key in assertion['style']:
                        if style_key in style:
                            if style[style_key]:
                                actual[style_key] = style[style_key].lower()
                            else:
                                actual[style_key] = style[style_key]
                        else:
                            actual[style_key] = ''

                    expected = assertion['style']

                    progress_character='.'

                    if actual != expected:

                        failure_trace = {
                            'assertion': assertion['assertion'],
                            'file': self.file,
                            'row': assertion['row'] + 1,
                            'col': col + 1,
                            'actual': actual,
                            'expected': expected,
                        }

                        debug_message('')
                        debug_message('----- Assertion FAILED! -----')
                        debug_message('')
                        debug_message('Trace: %s' % str(failure_trace))
                        debug_message('')

                        failures.append(failure_trace)

                        progress_character='F'

                    assertion_count += 1

                    output.append(progress_character, True if assertion_count % 80 == 0 else False)

            if len(self.assertions) > 0:
                output.append('')

        except:
            test_view.tearDown()
            raise

        test_view.tearDown()

        return {
            'assertions': assertion_count,
            'failures': failures
        }

class TestView(object):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.set_scratch(True)

    def tearDown(self):
        if self.view:
            self.view.close()

    def assign_syntax(self, syntax):
        self.view.assign_syntax(syntax)

    def assign_color(self, color):
        self.view.settings().set('color_scheme', color)

    def set_content(self, content):
        self.view.run_command('_color_scheme_unit_set_content', {'text': content})

    def get_content(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

class Style(object):

    def __init__(self, view):
        self.view = view
        self.parse_color_scheme_file(self.view.settings().get('color_scheme'))

    def at_point(self, point):
        return self.get_styles_for_scope(self.view.scope_name(point).strip())

    def parse_color_scheme_file(self, color_scheme_file):
        color_scheme_content = sublime.load_resource(color_scheme_file)
        color_scheme_dict = plistlib.readPlistFromBytes(bytes(color_scheme_content, 'UTF-8'))
        self.selectors_in_scheme = color_scheme_dict['settings']

    def get_styles_for_scope(self, scope):
        styles = dict()

        for scheme_selector in self.selectors_in_scheme:
            if 'scope' not in scheme_selector:
                styles.update(scheme_selector['settings'])

        matched_style = {'settings': {}, 'score': 0}
        for scheme_selector in self.selectors_in_scheme:
            if 'scope' in scheme_selector:
                score = sublime.score_selector(scope, scheme_selector['scope'])
                if score:
                    if score > matched_style['score']:
                        matched_style['score'] = score
                        matched_style['settings'] = scheme_selector['settings']

        styles.update(matched_style['settings'])

        return styles

def run_color_scheme_test(test):
    return ColorSchemeTest(test).run()

class _color_scheme_unit_set_content(sublime_plugin.TextCommand):

    def run(self, edit, text):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)

class OutputView(object):

    def __init__(self, clear = False):
        self.window = sublime.active_window()

        if clear:
            self.view = self.window.create_output_panel('exec')
            self.view.settings().set('result_file_regex', '^([^\n:]+):([0-9]+):([0-9]+)$')
        else:
            self.view = self.window.find_output_panel('exec')

        self.show()

    def show(self):
        self.window.run_command('show_panel', {'panel': 'output.exec'})

    def append(self, text, newline = True):
        if newline:
            text += "\n"

        self.view.run_command('append', {
            'characters': text,
            'force': True,
            'scroll_to_end': True
        })

class RunColorSchemeTestsCommand(sublime_plugin.WindowCommand):

    def run(self):

        output = OutputView(True)
        output.append('ColorSchemeUnit %s' % VERSION)
        output.append('')

        failures = []
        total_assertions = 0

        tests = sublime.find_resources('color_scheme_test*')

        for test in tests:
            test_result = run_color_scheme_test(test)

            failures += test_result['failures']
            total_assertions += test_result['assertions']

        if len(failures) > 0:

            output.append('')
            output.append('')
            output.append('There were %s failures:' % len(failures))
            output.append('')

            for i, failure in enumerate(failures, start=1):
                output.append('%d) %s' % (i, failure['assertion']))
                output.append('Failed asserting %s equals %s' % (str(failure['actual']), str(failure['expected'])))
                output.append('--- Expected')
                output.append('+++ Actual')
                output.append('@@ @@')
                output.append('{{diff}}')
                output.append('')
                output.append('%s:%d:%d' % (failure['file'], failure['row'], failure['col']))
                output.append('')

            output.append('FAILURES!')
            output.append('Tests: %d, Assertions: %d, Failures: %d.' % (len(tests), total_assertions, len(failures)))
        else:
            output.append('')
            output.append('')
            output.append('OK (%d tests, %d assertions)' % (len(tests), total_assertions))

if DEV_TOOLS:

    class ShowScopeNameAndStylesCommand(sublime_plugin.TextCommand):

        def run(self, edit):

            point = self.view.sel()[-1].b
            scope = self.view.scope_name(point)
            style = Style(self.view).at_point(point)

            style_html = '<ul>'

            if 'foreground' in style:
                style_html += "<li>foreground: %s</li>" % style['foreground']
                del style['foreground']

            if 'background' in style:
                style_html += "<li>background: %s</li>" % style['background']
                del style['background']

            if 'fontStyle' in style:
                style_html += "<li>fontStyle: %s</li>" % style['fontStyle']
                del style['fontStyle']

            for x in sorted(style):
                style_html += "<li>%s: %s</li>" % (x, style[x])

            style_html += '</ul>';

            html = """
                <style>
                * { margin: 0; padding: 0; }
                body { padding: 8; background-color: #f8f8f8; color: #222; }
                </style>
                <p>%s</p><p><a href="%s">Copy</a></p><br>%s
            """ % (scope.replace(' ', '<br>'), scope.rstrip(), style_html)

            def copy_to_clipboard(view, text):

                sublime.set_clipboard(text)
                view.hide_popup()
                sublime.status_message('Scope name copied to clipboard')

            self.view.show_popup(html, on_navigate=lambda x: copy_to_clipboard(self.view, x))

    class SetColorSchemeOnLoad(sublime_plugin.EventListener):

        def on_load_async(self, view):

            m = re.match('^COLOR TEST "(?P<color>[^"]+)" "(?P<syntax>[^"]+)"', view.substr(sublime.Region(0, view.size())))

            if not m:
                return

            view.settings().set('color_scheme', m.group('color'))
