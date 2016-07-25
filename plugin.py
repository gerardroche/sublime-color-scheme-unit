from threading import Thread
import unittest
import sublime
import sublime_plugin
import os
import re
import plistlib
from timeit import default_timer as timer

VERSION = '0.6.0-dev';

DEBUG_MODE=bool(os.getenv('SUBLIME_COLOR_SCHEME_UNIT_DEBUG'))

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

        m = re.match('^COLOR TEST "(?P<color>[^"]+)" "(?P<syntax>[^"]+)"\n', self.content)

        if not m:
            raise RuntimeError('Invalid COLOR TEST: first line')

        self.color = m.group('color')

        syntaxes_found = sublime.find_resources(m.group('syntax') + '.sublime-syntax')

        if len(syntaxes_found) == 0:
            syntaxes_found = sublime.find_resources(m.group('syntax') + '.tmLanguage')

        if len(syntaxes_found) > 1:
            raise RuntimeError('Invalid syntax: found more than one')

        if len(syntaxes_found) is not 1:
            raise RuntimeError('Invalid syntax: not found')

        self.syntax = syntaxes_found[0]
        self.content = self.content.replace('COLOR TEST "%s"\nSYNTAX TEST "%s"\n' % (self.color, self.syntax), '')

        self.assertions = []

        consecutive_test_lines = 0

        for line_number, line in enumerate(self.content.splitlines()):
            m = re.match('^(//|#|\<\!--)\s*(?P<repeat>\^+)(?: fg=(?P<fg>[^ ]+)?)?(?: bg=(?P<bg>[^ ]+)?)?(?: fs=(?P<fs>[^=]*)?)?$', line.lower().rstrip(' -->'))

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

    def run(self, output):

        assertion_count = 0
        failures = []

        test_view = TestView()
        test_view.setUp()

        try:
            test_view.assign_color(self.color)
            test_view.assign_syntax(self.syntax)
            test_view.set_content(self.content)

            style_util = Style(test_view.view)

            debug_message('running test: %s' % self.test)

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

        color_scheme = self.view.settings().get('color_scheme')
        color_scheme_resource = sublime.load_resource(color_scheme)
        color_scheme_plist = plistlib.readPlistFromBytes(bytes(color_scheme_resource, 'UTF-8'))
        self.color_scheme_plist_settings = color_scheme_plist['settings']

        self.default_style = dict()
        for color_scheme_plist_dict in self.color_scheme_plist_settings:
            if 'scope' not in color_scheme_plist_dict:
                self.default_style.update(color_scheme_plist_dict['settings'])

    def at_point(self, point):
        scope = self.view.scope_name(point).strip()

        last_selector_score = -1
        style = self.default_style.copy()
        for color_scheme_definition in self.color_scheme_plist_settings:
            if 'scope' in color_scheme_definition:
                score = sublime.score_selector(scope, color_scheme_definition['scope'])
                if score and score >= last_selector_score:
                    last_selector_score = score
                    style.update(color_scheme_definition['settings'])

        return style

def run_color_scheme_test(test, output):
    return ColorSchemeTest(test).run(output)

class _color_scheme_unit_set_content(sublime_plugin.TextCommand):

    def run(self, edit, text):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)

class OutputView(object):

    def __init__(self):
        self.window = sublime.active_window()

        self.view = self.window.create_output_panel('color_scheme_unit')
        self.view.settings().set('result_file_regex', '^([^\n:]+):([0-9]+):([0-9]+)$')

    def show(self):
        self.window.run_command('show_panel', {'panel': 'output.color_scheme_unit'})

    def append(self, text, newline = True):
        if newline:
            text += "\n"

        self.view.run_command('append', {
            'characters': text,
            'force': True,
            'scroll_to_end': True
        })

class RunColorSchemeTestCommand(sublime_plugin.WindowCommand):

    def run(self):
        if self.is_enabled():
            self.window.run_command('run_color_scheme_tests', {
                'test_file': self.window.active_view().file_name()
            })

    def is_enabled(self):
        view = self.window.active_view()

        if not view:
            return False

        fname = view.file_name()
        if not fname:
            return False

        if re.match('.+/color_scheme_test.*\.[a-z]+$', fname):
            return True

        return False

class RunColorSchemeTestsCommand(sublime_plugin.WindowCommand):

    def run(self, test_file = None):
        sublime.set_timeout_async(lambda: self.run_async(test_file), 100)

    def run_async(self, test_file):

        output = OutputView()
        output.append('ColorSchemeUnit %s' % VERSION)
        output.append('')
        output.show()

        failures = []
        total_assertions = 0

        tests = sublime.find_resources('color_scheme_test*')

        test_files = []
        if test_file:
            for test in tests:
                abs_test = os.path.join(os.path.dirname(sublime.packages_path()), test)
                if test_file == abs_test:
                    test_files = [test]
                    break

        if len(test_files) > 0:
            tests = test_files

        start = timer()

        for test in tests:
            test_result = run_color_scheme_test(test, output)

            failures += test_result['failures']
            total_assertions += test_result['assertions']

        elapsed = timer() - start

        if len(failures) > 0:

            output.append('')
            output.append('Time: %.2f secs' % (elapsed))
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
            output.append('Time: %.2f secs' % (elapsed))
            output.append('')
            output.append('OK (%d tests, %d assertions)' % (len(tests), total_assertions))

if DEBUG_MODE:

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
