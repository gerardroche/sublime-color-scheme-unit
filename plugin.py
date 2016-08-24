from threading import Thread
import unittest
import sublime
import sublime_plugin
import os
import re
import plistlib
from timeit import default_timer as timer

VERSION = '0.9.0';
DEBUG=bool(os.getenv('SUBLIME_COLOR_SCHEME_UNIT_DEBUG'))

if DEBUG:
    def debug_message(message):
        print('DEBUG [color_scheme_unit] %s' % str(message))
else:
    def debug_message(message):
        pass

class TestView(object):

    def __init__(self, name, window):
        self.name = name + '_test_view'
        self.window = window

    def setUp(self):
        self.view = self.window.create_output_panel(self.name, True)

    def tearDown(self):
        if self.view:
            self.view.close()

    def set_content(self, content):
        # TODO is there a way to avoid running the following superfluous text command?
        self.view.run_command('_set_content', {'content': content})

    def get_content(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

class _set_content(sublime_plugin.TextCommand):

    """
    Helper view command for TextView#set_content()
    """

    def run(self, edit, content):
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, content)

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

COLOR_TEST_PARAMS_COMPILED_PATTERN = re.compile('^(?:(?:\<\?php )?(?://|#|\/\*|\<\!--)\s*)?COLOR TEST "(?P<color_scheme>[^"]+)" "(?P<syntax_name>[^"]+)"(?:\s*(?:--\>|\*\/))?\n')
COLOR_TEST_ASSERTION_COMPILED_PATTERN = re.compile('^(//|#|\/\*|\<\!--)\s*(?P<repeat>\^+)(?: fg=(?P<fg>[^ ]+)?)?(?: bg=(?P<bg>[^ ]+)?)?(?: fs=(?P<fs>[^=]*)?)?$')

def run_color_scheme_test(test, window, output):
    debug_message('running color scheme test: %s' % test)

    error = False
    failures = []
    assertion_count = 0

    test_view = TestView('color_scheme_unit', window)
    test_view.setUp()

    try:
        test_content = sublime.load_resource(test)

        color_test_params = COLOR_TEST_PARAMS_COMPILED_PATTERN.match(test_content)

        if not color_test_params:
            error = {
                'message': 'Invalid color test',
                'file': os.path.join(os.path.dirname(sublime.packages_path()), test),
                'row': 0,
                'col': 0
            }
            raise RuntimeError(error['message'])

        syntaxes = sublime.find_resources(color_test_params.group('syntax_name') + '.sublime-syntax')

        if len(syntaxes) > 1:
            error = {
                'message': 'Too many syntaxes found',
                'file': os.path.join(os.path.dirname(sublime.packages_path()), test),
                'row': 0,
                'col': 0
            }
            raise RuntimeError(error['message'])

        if len(syntaxes) is not 1:
            error = {
                'message': 'Syntaxes not found',
                'file': os.path.join(os.path.dirname(sublime.packages_path()), test),
                'row': 0,
                'col': 0
            }
            raise RuntimeError(error['message'])

        test_view.view.settings().set('color_scheme', color_test_params.group('color_scheme'))
        test_view.view.assign_syntax(syntaxes[0])
        test_view.set_content(test_content)

        color_scheme_style = ColorSchemeStyle(test_view.view)

        consecutive_test_lines = 0
        for line_number, line in enumerate(test_content.splitlines()):
            assertion_params = COLOR_TEST_ASSERTION_COMPILED_PATTERN.match(line.lower().rstrip(' -->').rstrip(' */'))
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

                    debug_message('----- Assertion FAILED! -----')
                    debug_message('Trace: %s' % str(failure_trace))

                    failures.append(failure_trace)

                output.write(progress_character)
                if assertion_count % 80 == 0:
                    output.write("\n")

        output.write("\n")
    except Exception as e:
        test_view.tearDown()
        if not error:
            output.write(str(e))
            output.write("\n")

    test_view.tearDown()

    return {
        'error': error,
        'failures': failures,
        'assertions': assertion_count
    }

class TestOutputPanel(object):

    def __init__(self, name, window):
        self.view = window.create_output_panel(name)

        settings = self.view.settings()
        settings.set('result_file_regex', '^(.+):([0-9]+):([0-9]+)$')
        settings.set('word_wrap', False)
        settings.set('line_numbers', False)
        settings.set('gutter', False)
        settings.set('rulers', [])
        settings.set('scroll_past_end', False)

        # Assign syntax
        self.view.assign_syntax('Packages/color_scheme_unit/test_output_panel.sublime-syntax')

        # Assign the active color scheme
        active_view = window.active_view()
        if active_view:
            active_color_scheme = active_view.settings().get('color_scheme')
            if active_color_scheme:
                settings.set('color_scheme', active_color_scheme)

        window.run_command(
            'show_panel', {
                'panel': 'output.' + name
            }
        )

    def write(self, text):
        self.view.run_command(
            'append', {
                'characters': text,
                'scroll_to_end': True
            }
        )

class RunColorSchemeTestCommand(sublime_plugin.WindowCommand):

    def run(self):
        if not self.is_enabled():
            return

        view = self.window.active_view()
        if not view:
            return

        self.window.run_command(
            'run_color_scheme_tests', {
                'test_file': view.file_name()
            }
        )

    def is_enabled(self):
        view = self.window.active_view()
        if not view:
            return False

        file_name = view.file_name()
        if not file_name:
            return False

        if not re.match('^.+/color_scheme_test.*\.[a-z]+$', file_name):
            return False

        return True

class RunColorSchemeTestsCommand(sublime_plugin.WindowCommand):

    def run(self, test_file = None):
        sublime.set_timeout_async(lambda: self.run_async(test_file))

    def run_async(self, test_file):
        view = self.window.active_view()
        if not view:
            return

        file_name = view.file_name()
        if not file_name:
            return

        tests = []
        for resource in sublime.find_resources('color_scheme_test*'):
            package = resource.split(os.sep)[1]
            package_path = os.path.join(sublime.packages_path(), package)
            if file_name.startswith(package_path):
                tests_package_name = package
                if test_file:
                    resource_file = os.path.join(os.path.dirname(sublime.packages_path()), resource)
                    if test_file == resource_file:
                        tests.append(resource)
                else:
                    tests.append(resource)

        if not len(tests):
            return

        output = TestOutputPanel('color_scheme_unit', self.window)
        output.write("ColorSchemeUnit %s\n\n" % VERSION)
        output.write("Runtime: %s build %s\n" % (sublime.platform(), sublime.version()))
        output.write("Package: %s\n" % tests_package_name)
        if test_file:
            output.write("File:    %s\n" % test_file)
        output.write("\n")

        errors = []
        failures = []
        total_assertions = 0

        start = timer()
        for test in tests:
            test_result = run_color_scheme_test(test, self.window, output)
            if test_result['error']:
                errors += [test_result['error']]
            failures += test_result['failures']
            total_assertions += test_result['assertions']
        elapsed = timer() - start
        output.write("\n")

        output.write("Time: %.2f secs\n" % (elapsed))
        output.write("\n")

        if len(errors) > 0:
            output.write("There were %s errors:\n" % len(errors))
            output.write("\n")
            for i, error in enumerate(errors, start=1):
                output.write("%d) %s\n" % (i, error['message']))
                output.write("%s:%d:%d\n" % (error['file'], error['row'], error['col']))
                output.write("\n")

        if len(failures) > 0:
            output.write("There were %s failures:\n\n" % len(failures))
            for i, failure in enumerate(failures, start=1):
                output.write("%d) %s\n" % (i, failure['assertion']))
                output.write("Failed asserting %s equals %s\n" % (str(failure['actual']), str(failure['expected'])))
                # TODO failure diff
                # output.write("--- Expected\n")
                # output.write("+++ Actual\n")
                # output.write("@@ @@\n")
                # output.write("{{diff}}\n\n")
                output.write("%s:%d:%d\n" % (failure['file'], failure['row'], failure['col']))
                output.write("\n")

        if len(errors) == 0 and len(failures) == 0:
            output.write("OK (%d tests, %d assertions)\n" % (len(tests), total_assertions))
        else:
            output.write("FAILURES!\n")
            output.write("Tests: %d, Assertions: %d" % (len(tests), total_assertions))
            if len(errors) > 0:
                output.write(", Errors: %d" % (len(errors)))
            output.write(", Failures: %d" % (len(failures)))
            output.write(".")
            output.write("\n")

if DEBUG:

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
            color_test_params = COLOR_TEST_PARAMS_COMPILED_PATTERN.match(view.substr(sublime.Region(0, view.size())))
            if color_test_params:
                view.settings().set('color_scheme', color_test_params.group('color_scheme'))
