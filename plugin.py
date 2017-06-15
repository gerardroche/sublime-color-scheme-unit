import os
import re
import plistlib
from timeit import default_timer as timer

import sublime
import sublime_plugin

__version__ = "1.2.0"
__version_info__ = (1, 2, 0)

_COLOR_TEST_PARAMS_COMPILED_PATTERN = re.compile('^(?:(?:\<\?php )?(?://|#|\/\*|\<\!--)\s*)?COLOR SCHEME TEST "(?P<color_scheme>[^"]+)" "(?P<syntax_name>[^"]+)"(?:\s*(?:--\>|\?\>|\*\/))?')  # noqa: E501
_COLOR_TEST_ASSERTION_COMPILED_PATTERN = re.compile('^(//|#|\/\*|\<\!--)\s*(?P<repeat>\^+)(?: fg=(?P<fg>[^ ]+)?)?(?: bg=(?P<bg>[^ ]+)?)?(?: fs=(?P<fs>[^=]*)?)?$')  # noqa: E501


class TestView():

    def __init__(self, name, window):
        self.name = name + '_test_view'
        self.window = window

    def setUp(self):
        self.view = self.window.create_output_panel(self.name, unlisted=True)

    def tearDown(self):
        if self.view:
            self.view.close()

    def set_content(self, content):
        self.view.run_command('color_scheme_unit_set_view_content', {
            'content': content
        })

    def get_content(self):
        return self.view.substr(sublime.Region(0, self.view.size()))


class TestOutputPanel():

    def __init__(self, name, window):
        self.view = window.create_output_panel(name)

        settings = self.view.settings()
        settings.set('result_file_regex', '^(.+):([0-9]+):([0-9]+)$')
        settings.set('word_wrap', False)
        settings.set('line_numbers', False)
        settings.set('gutter', False)
        settings.set('rulers', [])
        settings.set('scroll_past_end', False)

        self.view.assign_syntax('Packages/color_scheme_unit/res/text-ui-result.sublime-syntax')

        active_view = window.active_view()
        if active_view:
            active_color_scheme = active_view.settings().get('color_scheme')
            if active_color_scheme:
                settings.set('color_scheme', active_color_scheme)

        window.run_command('show_panel', {'panel': 'output.' + name})

    def write(self, text):
        self.view.run_command('append', {'characters': text, 'scroll_to_end': True})


class ColorSchemeStyle():

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

        style = self.default_style.copy()
        scored_styles = []
        for color_scheme_definition in self.color_scheme_plist_settings:
            if 'scope' in color_scheme_definition:
                score = sublime.score_selector(scope, color_scheme_definition['scope'])
                if score:
                    color_scheme_definition.update({'score': score})
                    scored_styles.append(color_scheme_definition)

        for s in sorted(scored_styles, key=lambda k: k['score']):
            style.update(s['settings'])

        return style


class ResultPrinter():

    def __init__(self, output, debug=True):
        self.assertions = 0
        self.tests = 0
        self.tests_total = 0
        self.output = output
        self.debug = debug

    def _wrap_progress(self):
        if self.assertions % 80 == 0:
            self.output.write(' %d / %s (%6.2f%%)\n' % (
                self.tests,
                self.tests_total,
                (self.tests / self.tests_total) * 100)
            )

    def on_tests_start(self, tests):
        self.tests_total = len(tests)
        self.start_time = timer()

    def on_tests_end(self):
        self.output.write('\n\n')
        self.output.write('Time: %.2f secs\n' % (timer() - self.start_time))
        self.output.write('\n')

    def on_test_start(self, test, data):
        if self.debug:
            self.output.write('\n\nStarting test \'{}\'\n  color scheme: \'{}\'\n  syntax: \'{}\'\n\n'
                              .format(test, data['color_scheme'], data['syntax']))

    def on_test_end(self):
        self.tests += 1

    def on_assertion_success(self):
        self.output.write('.')
        self.assertions += 1
        self._wrap_progress()

    def on_assertion_failure(self, failure_trace):
        self.output.write('F')
        self.assertions += 1

        # if self.debug:
        #     self.output.write('\nFailure trace: %s\n' % str(failure_trace))

        self._wrap_progress()


def run_color_scheme_test(test, window, result_printer):
    error = False
    failures = []
    assertion_count = 0

    test_view = TestView('color_scheme_unit', window)
    test_view.setUp()

    try:
        test_content = sublime.load_resource(test)

        color_test_params = _COLOR_TEST_PARAMS_COMPILED_PATTERN.match(test_content)
        if not color_test_params:
            error = {
                'message': 'Invalid color scheme test: unable to find valid COLOR SCHEME TEST marker',
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

        color_scheme = 'Packages/' + color_test_params.group('color_scheme')
        syntax = syntaxes[0]

        # This is down here rather than at the start of the function so that the
        # on_test_start method will have extra information like the color
        # scheme and syntax to print out if debugging is enabled.
        result_printer.on_test_start(test, {
            'color_scheme': color_scheme,
            'syntax': syntax
        })

        test_view.view.settings().set('color_scheme', color_scheme)
        test_view.view.assign_syntax(syntax)
        test_view.set_content(test_content)

        color_scheme_style = ColorSchemeStyle(test_view.view)

        consecutive_test_lines = 0
        for line_number, line in enumerate(test_content.splitlines()):
            assertion_params = _COLOR_TEST_ASSERTION_COMPILED_PATTERN.match(line.lower().rstrip(' -->').rstrip(' */'))
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

                if actual_styles == expected_styles:
                    result_printer.on_assertion_success()
                else:

                    failure_trace = {
                        'assertion': assertion,
                        'file': os.path.join(os.path.dirname(sublime.packages_path()), test),
                        'row': assertion_row + 1,
                        'col': col + 1,
                        'actual': actual_styles,
                        'expected': expected_styles,
                    }

                    result_printer.on_assertion_failure(failure_trace)

                    failures.append(failure_trace)

    except Exception as e:
        if not error:
            result_printer.write("\nAn error occurred: %s\n" % str(e))
    finally:
        test_view.tearDown()

    result_printer.on_test_end()

    return {
        'error': error,
        'failures': failures,
        'assertions': assertion_count
    }


def is_valid_color_scheme_test_file_name(file_name):
    return bool(re.match('^color_scheme_test.*\.[a-zA-Z0-9]+$', os.path.basename(file_name)))


class ColorSchemeUnit():

    def __init__(self, window):
        self.window = window
        self.view = self.window.active_view()
        if not self.view:
            raise ValueError('view not found')

    def run_file(self):
        file = self.view.file_name()
        if file:
            if is_valid_color_scheme_test_file_name(file):
                self.run(file=file)
            else:
                return sublime.status_message('ColorSchemeUnit: file name not a valid test file name')
        else:
            return sublime.status_message('ColorSchemeUnit: file not found')

    def run(self, file=None):
        sublime.set_timeout_async(lambda: self.run_async(file))

    def run_async(self, test_file):
        file_name = self.view.file_name()
        if not file_name:
            return sublime.status_message('ColorSchemeUnit: file not found')

        def normalise_resource_path(path):
            if sublime.platform() == 'windows':
                path = re.sub(r"/", r"\\", path)
            return path

        tests = []
        for resource in sublime.find_resources('color_scheme_test*'):
            package = resource.split('/')[1]
            package_path = os.path.join(sublime.packages_path(), package)
            if file_name.startswith(package_path):
                tests_package_name = package
                if test_file:
                    resource_file = os.path.join(
                        os.path.dirname(sublime.packages_path()),
                        normalise_resource_path(resource)
                    )
                    if test_file == resource_file:
                        tests.append(resource)
                else:
                    tests.append(resource)

        if not len(tests):
            print("ColorSchemeUnit: no test found; be sure run tests from within the packages directory")
            return sublime.status_message(
                "ColorSchemeUnit: no test found; be sure run tests from within the packages directory"
            )

        output = TestOutputPanel('color_scheme_unit', self.window)
        output.write("ColorSchemeUnit %s\n\n" % __version__)
        output.write("Runtime: %s build %s\n" % (sublime.platform(), sublime.version()))
        output.write("Package: %s\n" % tests_package_name)
        if test_file:
            output.write("File:    %s\n" % test_file)
        output.write("\n")

        result_printer = ResultPrinter(output, debug=self.view.settings().get('color_scheme_unit.debug'))

        errors = []
        failures = []
        total_assertions = 0

        result_printer.on_tests_start(tests)
        for i, test in enumerate(tests):
            test_result = run_color_scheme_test(test, self.window, result_printer)
            if test_result['error']:
                errors += [test_result['error']]
            failures += test_result['failures']
            total_assertions += test_result['assertions']
        result_printer.on_tests_end()

        if len(errors) > 0:
            output.write("There %s %s errors%s:\n\n" % (
                'was' if len(errors) == 1 else 'were',
                len(errors),
                '' if len(errors) == 1 else 's',
            ))
            output.write("\n")
            for i, error in enumerate(errors, start=1):
                output.write("%d) %s\n" % (i, error['message']))
                output.write("%s:%d:%d\n" % (error['file'], error['row'], error['col']))
                output.write("\n")

        if len(failures) > 0:
            output.write("There %s %s failure%s:\n\n" % (
                'was' if len(failures) == 1 else 'were',
                len(failures),
                '' if len(failures) == 1 else 's',
            ))

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


class ColorSchemeUnitShowScopeNameAndStylesCommand(sublime_plugin.TextCommand):

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
            sublime.set_clipboard(text)
            view.hide_popup()
            sublime.status_message('Scope name copied to clipboard')

        self.view.show_popup(html, max_width=512, max_height=700, on_navigate=lambda x: copy(self.view, x))


class ColorSchemeUnitSetColorSchemeOnLoadEvent(sublime_plugin.EventListener):

    def on_load_async(self, view):
        file_name = view.file_name()
        if file_name:
            if is_valid_color_scheme_test_file_name(file_name):
                color_scheme_params = _COLOR_TEST_PARAMS_COMPILED_PATTERN.match(
                    view.substr(sublime.Region(0, view.size()))
                )
                if color_scheme_params:
                    view.settings().set('color_scheme', 'Packages/' + color_scheme_params.group('color_scheme'))


class ColorSchemeUnitSetViewContent(sublime_plugin.TextCommand):

    def run(self, edit, content):
        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, content)


class ColorSchemeUnitTestFileCommand(sublime_plugin.WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run_file()


class ColorSchemeUnitTestSuiteCommand(sublime_plugin.WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run()


class ColorSchemeUnitTestResultsCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.run_command('show_panel', {'panel': 'output.color_scheme_unit'})
