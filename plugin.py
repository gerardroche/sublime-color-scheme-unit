from threading import Thread
import unittest
import sublime
import sublime_plugin
import os
import re
import plistlib
from timeit import default_timer as timer

VERSION = '0.6.0';

DEBUG_MODE=bool(os.getenv('SUBLIME_COLOR_SCHEME_UNIT_DEBUG'))

if DEBUG_MODE:
    def debug_message(message):
        print('DEBUG [color_scheme_unit] %s' % str(message))
else:
    def debug_message(message):
        pass

class TestView(object):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        self.view.set_scratch(True)

    def tearDown(self):
        if self.view:
            self.view.close()

    def assign_syntax(self, syntax):
        self.view.assign_syntax(syntax)

    def assign_color_scheme(self, color_scheme):
        self.view.settings().set('color_scheme', color_scheme)

    def set_content(self, content):
        self.view.run_command('append', {'characters': content})

    def get_content(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

class ColorSchemeStyle(object):

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
    debug_message('running test: %s' % test)

    error = False
    failures = []
    assertion_count = 0

    test_view = TestView()
    test_view.setUp()

    try:
        test_content = sublime.load_resource(test)

        color_test_params = re.match('^(?:(?:\<\?php )?(?://|#|\<\!--)\s*)?COLOR TEST "(?P<color_scheme>[^"]+)" "(?P<syntax_name>[^"]+)"\n', test_content)
        if not color_test_params:
            error = {
                'message': 'Invalid color test',
                'file': os.path.join(os.path.dirname(sublime.packages_path()), test),
                'row': 0,
                'col': 0
            }

            raise RuntimeError(error['message'])

        test_color_scheme = color_test_params.group('color_scheme')

        syntaxes = sublime.find_resources(color_test_params.group('syntax_name') + '.sublime-syntax')
        if len(syntaxes) == 0: # fallback to old syntax
            syntaxes = sublime.find_resources(color_test_params.group('syntax_name') + '.tmLanguage')
        if len(syntaxes) > 1:
            raise RuntimeError('Invalid syntax: found more than one')
        if len(syntaxes) is not 1:
            raise RuntimeError('Invalid syntax: not found')
        test_syntax = syntaxes[0]

        test_view.assign_syntax(test_syntax)
        test_view.assign_color_scheme(test_color_scheme)
        test_view.set_content(test_content)

        color_scheme_style = ColorSchemeStyle(test_view.view)

        consecutive_test_lines = 0
        for line_number, line in enumerate(test_content.splitlines()):
            assertion_params = re.match('^(//|#|\<\!--)\s*(?P<repeat>\^+)(?: fg=(?P<fg>[^ ]+)?)?(?: bg=(?P<bg>[^ ]+)?)?(?: fs=(?P<fs>[^=]*)?)?$', line.lower().rstrip(' -->'))
            if not assertion_params:
                consecutive_test_lines = 0
                continue

            consecutive_test_lines += 1

            assertion = assertion_params.group(0)
            assertion_row = line_number - consecutive_test_lines
            assertion_begin = line.find('^')
            assertion_end = assertion_begin + len(assertion_params.group('repeat'))
            expected_styles = {}
            if assertion_params.group('fg') is not None:
                expected_styles['foreground'] = assertion_params.group('fg')
            if assertion_params.group('bg') is not None:
                expected_styles['background'] = assertion_params.group('bg')
            if assertion_params.group('fs') is not None:
                expected_styles['fontStyle'] = assertion_params.group('fs')

            for col in range(assertion_begin, assertion_end):
                assertion_count += 1
                assertion_point = test_view.view.text_point(assertion_row, col)
                actual_styles_at_point = color_scheme_style.at_point(assertion_point)

                actual_styles = {}
                for style in expected_styles:
                    if style in actual_styles_at_point:
                        if actual_styles_at_point[style]:
                            actual_styles[style] = actual_styles_at_point[style].lower()
                        else:
                            actual_styles[style] = actual_styles_at_point[style]
                    else:
                        actual_styles[style] = ''

                progress_character='.'
                if actual_styles != expected_styles:
                    progress_character='F'

                    failure_trace = {
                        'assertion': assertion,
                        'file': os.path.join(os.path.dirname(sublime.packages_path()), test),
                        'row': assertion_row + 1,
                        'col': col + 1,
                        'actual': actual_styles,
                        'expected': expected_styles,
                    }

                    debug_message('')
                    debug_message('----- Assertion FAILED! -----')
                    debug_message('')
                    debug_message('Trace: %s' % str(failure_trace))
                    debug_message('')

                    failures.append(failure_trace)

                output.append(progress_character)
                if assertion_count % 80 == 0:
                    output.append("\n")

        output.append("\n")
    except Exception as e:
        test_view.tearDown()
        if not error:
            output.append(str(e))

    test_view.tearDown()

    return {
        'error': error,
        'failures': failures,
        'assertions': assertion_count
    }

class OutputPanel(object):

    def __init__(self):
        self.window = sublime.active_window()

        self.output_view = self.window.create_output_panel('color_scheme_unit')

        output_view_settings = self.output_view.settings()
        output_view_settings.set('result_file_regex', '^(.+):([0-9]+):([0-9]+)$')
        output_view_settings.set("word_wrap", False)
        output_view_settings.set("line_numbers", False)
        output_view_settings.set("gutter", False)
        output_view_settings.set("rulers", [])
        output_view_settings.set("scroll_past_end", False)

        self.output_view.assign_syntax('Packages/color_scheme_unit/test_result.sublime-syntax')

        view = self.window.active_view()
        if view:
            color_scheme = view.settings().get('color_scheme')
            if color_scheme:
                output_view_settings.set('color_scheme', color_scheme)

    def show(self):
        self.window.run_command('show_panel', {'panel': 'output.color_scheme_unit'})

    def append(self, text):
        self.output_view.run_command('append', {
            'characters': text,
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

        output = OutputPanel()
        output.append("color_scheme_unit %s\n\n" % VERSION)
        output.show()

        errors = []
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
            if test_result['error']:
                errors += [test_result['error']]
            failures += test_result['failures']
            total_assertions += test_result['assertions']

        elapsed = timer() - start

        output.append("\nTime: %.2f secs\n" % (elapsed))

        if len(errors) > 0:
            output.append("\nThere were %s errors:\n\n" % len(errors))
            for i, error in enumerate(errors, start=1):
                output.append("%d) %s\n" % (i, error['message']))
                output.append("%s:%d:%d\n\n" % (error['file'], error['row'], error['col']))

        if len(failures) > 0:

            output.append("\nThere were %s failures:\n\n" % len(failures))

            for i, failure in enumerate(failures, start=1):
                output.append("%d) %s\n" % (i, failure['assertion']))
                output.append("Failed asserting %s equals %s\n" % (str(failure['actual']), str(failure['expected'])))
                output.append("--- Expected\n")
                output.append("+++ Actual\n")
                output.append("@@ @@\n")
                output.append("{{diff}}\n\n")
                output.append("%s:%d:%d\n\n" % (failure['file'], failure['row'], failure['col']))

        if len(errors) == 0 and len(failures) == 0:
            output.append("\nOK (%d tests, %d assertions)\n" % (len(tests), total_assertions))
        else:
            output.append("FAILURES!\n")

            output.append("Tests: %d, Assertions: %d" % (len(tests), total_assertions))

            if len(errors) > 0:
                output.append(", Errors: %d" % (len(errors)))

            output.append(", Failures: %d" % (len(failures)))

            output.append(".\n")

if DEBUG_MODE:

    class ShowScopeNameAndStylesCommand(sublime_plugin.TextCommand):

        def run(self, edit):
            point = self.view.sel()[-1].b
            scope = self.view.scope_name(point)
            style = ColorSchemeStyle(self.view).at_point(point)

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
            color_test_params = re.match('^COLOR TEST "(?P<color>[^"]+)" "(?P<syntax>[^"]+)"', view.substr(sublime.Region(0, view.size())))
            if color_test_params:
                view.settings().set('color_scheme', color_test_params.group('color'))
