import os
import re

from sublime import find_resources
from sublime import load_resource
from sublime import packages_path
from sublime import platform
from sublime import Region
from sublime import set_timeout_async
from sublime import status_message
from sublime import version

from ColorSchemeUnit.lib.color_scheme import ViewStyle
from ColorSchemeUnit.lib.coverage import Coverage
from ColorSchemeUnit.lib.result import ResultPrinter
from ColorSchemeUnit.lib.test import TestOutputPanel
from ColorSchemeUnit.lib.test import TestView


__version__ = "2.0.0"

__version_info__ = (2, 0, 0)

_color_test_params_compiled_pattern = re.compile(
    '^(?:(?:\\<\\?php )?(?://|#|\\/\\*|\\<\\!--|--)\\s*)?'
    'COLOR SCHEME TEST "(?P<color_scheme>[^"]+)"'
    '(?:(?P<skip_if_not_syntax> SKIP IF NOT)? "(?P<syntax_name>[^"]+)")?'
    '(?:\\s*(?:--\\>|\\?\\>|\\*\\/))?')

_color_test_assertion_compiled_pattern = re.compile(
    '^\\s*(//|#|\\/\\*|\\<\\!--|--)\\s*'
    '(?P<repeat>\\^+)'
    '(?: fg=(?P<fg>[^ ]+)?)?'
    '(?: bg=(?P<bg>[^ ]+)?)?'
    '(?: fs=(?P<fs>[^=]*)?)?'
    '(?: build\\>=(?P<build>[^=]*)?)?'
    '$')


def message(msg):
    msg = 'ColorSchemeUnit: {}'.format(msg)
    status_message(msg)
    print(msg)


def is_valid_color_scheme_test_file_name(file_name):
    if not file_name:
        return False

    return bool(re.match('^color_scheme_test.*\\.[a-zA-Z0-9]+$', os.path.basename(file_name)))


def get_color_scheme_test_params_color_scheme(view):
    params = get_color_scheme_test_params(view.substr(Region(0, view.size())))
    if params:
        return params['color_scheme']


def get_color_scheme_test_params(test_content: str):
    color_test_params = _color_test_params_compiled_pattern.match(test_content)
    if color_test_params:
        if color_test_params.group('color_scheme').endswith('.sublime-color-scheme'):
            color_scheme = color_test_params.group('color_scheme')
            if '/' in color_scheme and not color_scheme.startswith('Packages'):
                color_scheme = 'Packages/' + color_scheme
        else:
            color_scheme = 'Packages/' + color_test_params.group('color_scheme')

        return {
            'syntax_name': color_test_params.group('syntax_name'),
            'skip_if_not_syntax': color_test_params.group('skip_if_not_syntax'),
            'color_scheme': color_scheme
        }

    return None


def run_color_scheme_test(test, window, result_printer, code_coverage):
    skip = {}  # type: dict
    error = {}  # type: dict
    failures = []
    assertion_count = 0

    test_view = TestView(window, test)
    test_view.setUp()

    try:
        test_content = load_resource(test)

        color_test_params = get_color_scheme_test_params(test_content)
        if not color_test_params:
            err_msg = 'Invalid COLOR SCHEME TEST header'
            error['message'] = err_msg
            error['file'] = test_view.file_name()
            error['row'] = 0
            error['col'] = 0
            raise RuntimeError(err_msg)

        syntax_package_name = None
        syntax = color_test_params['syntax_name']
        if not syntax:
            syntax = os.path.splitext(test)[1].lstrip('.').upper()
        elif '/' in syntax:
            syntax_package_name, syntax = syntax.split('/')

        syntaxes = find_resources(syntax + '.sublime-syntax')
        if not syntaxes:
            syntaxes = find_resources(syntax + '.tmLanguage')
            if not syntaxes:
                syntaxes = find_resources(syntax + '.hidden-tmLanguage')

        if syntax_package_name:
            syntaxes = [s for s in syntaxes if syntax_package_name in s]

        if len(syntaxes) > 1:
            err_msg = 'More than one syntax found: {}'.format(syntaxes)
            error['message'] = err_msg
            error['file'] = test_view.file_name()
            error['row'] = 0
            error['col'] = 0
            raise RuntimeError(err_msg)

        if len(syntaxes) != 1:
            if color_test_params['skip_if_not_syntax']:
                err_msg = 'Syntax not found: {}'.format(syntax)
                skip['message'] = err_msg
                skip['file'] = test_view.file_name()
                skip['row'] = 0
                skip['col'] = 0
                raise RuntimeError(err_msg)
            else:
                err_msg = 'Syntax not found: {}'.format(syntax)
                error['message'] = err_msg
                error['file'] = test_view.file_name()
                error['row'] = 0
                error['col'] = 0
                raise RuntimeError(err_msg)

        test_view.view.assign_syntax(syntaxes[0])
        test_view.view.settings().set('color_scheme', color_test_params['color_scheme'])
        test_view.set_content(test_content)

        color_scheme_style = ViewStyle(test_view.view)

        # This is down here rather than at the start of the function so that the
        # on_test_start method will have extra information like the color
        # scheme and syntax to print out if debugging is enabled.
        result_printer.on_test_start(test, test_view)
        code_coverage.on_test_start(test, test_view)

        consecutive_test_lines = 0
        for line_number, line in enumerate(test_content.splitlines()):
            has_failed_assertion = False
            assertion_params = _color_test_assertion_compiled_pattern.match(line.lower().rstrip(' -->').rstrip(' */'))
            if not assertion_params:
                consecutive_test_lines = 0
                continue

            consecutive_test_lines += 1

            requires_build = assertion_params.group('build')
            if requires_build:
                if int(version()) < int(requires_build):
                    continue

            assertion_row = line_number - consecutive_test_lines
            assertion_begin = line.find('^')
            assertion_repeat = assertion_params.group('repeat')
            assertion_end = assertion_begin + len(assertion_repeat)
            assertion_fg = assertion_params.group('fg')
            assertion_bg = assertion_params.group('bg')
            assertion_fs = assertion_params.group('fs')

            expected = {}

            if assertion_fg is not None:
                expected['foreground'] = assertion_fg

            if assertion_bg is not None:
                expected['background'] = assertion_bg

            if assertion_fs is not None:
                expected['fontStyle'] = assertion_fs

            for col in range(assertion_begin, assertion_end):
                result_printer.on_assertion()
                assertion_count += 1
                assertion_point = test_view.view.text_point(assertion_row, col)
                actual_styles = color_scheme_style.at_point(assertion_point)

                actual = {}
                for style in expected:
                    if style in actual_styles:
                        if actual_styles[style]:
                            actual[style] = actual_styles[style].lower()
                        else:
                            actual[style] = actual_styles[style]
                    else:
                        actual[style] = ''

                if 'fontStyle' in actual and actual['fontStyle'] == 'none':
                    actual['fontStyle'] = ''

                if actual != expected:
                    has_failed_assertion = True
                    failures.append({
                        'assertion': assertion_params.group(0),
                        'file': test_view.file_name(),
                        'row': assertion_row + 1,
                        'col': col + 1,
                        'actual': actual,
                        'expected': expected,
                    })

            if has_failed_assertion:
                result_printer.on_test_failure()
            else:
                result_printer.on_test_success()

    except Exception as e:
        if not error and not skip:
            result_printer.output.write("\nAn error occurred: %s\n" % str(e))

        if error:
            result_printer.addError(test, test_view)

        if skip:
            result_printer.addSkippedTest(test, test_view)

    finally:
        test_view.tearDown()

    result_printer.on_test_end()

    return {
        'skip': skip,
        'error': error,
        'failures': failures,
        'assertions': assertion_count
    }


class ColorSchemeUnit():

    def __init__(self, window):
        self.window = window
        self.view = self.window.active_view()
        if not self.view:
            raise ValueError('view not found')

    def run_file(self):
        file = self.view.file_name()
        if file:
            file = os.path.realpath(file)
            if is_valid_color_scheme_test_file_name(file):
                self.run(file=file)
            else:
                return status_message('ColorSchemeUnit: file name not a valid test file name')
        else:
            return status_message('ColorSchemeUnit: file not found')

    def results(self):
        self.window.run_command('show_panel', {'panel': 'output.color_scheme_unit'})

    def run(self, package=None, file=None, output=None, **kwargs):
        is_async = kwargs.get('async', True)
        if is_async:
            set_timeout_async(lambda: self._run(package, file, output), 100)
        else:
            return self._run(package, file, output, is_async=is_async)

    def _run(self, package=None, file=None, output=None, is_async=True):
        if package and file:
            raise TypeError('package or file, but not both')

        unittesting = True if output else False

        tests = []

        resources = find_resources('color_scheme_test*')

        if file:
            file = os.path.realpath(file)
            ppr = os.path.dirname(packages_path())
            for resource in resources:
                if file == os.path.realpath(os.path.join(ppr, resource)):
                    tests.append(resource)
        else:
            if not package:
                package_file = self.view.file_name()
                if not package_file:
                    return message('package file not found')

                package_file = os.path.realpath(package_file)
                for resource_package in set(t.split('/')[1] for t in resources):
                    if package_file.startswith(os.path.realpath(os.path.join(packages_path(), resource_package))):
                        package = resource_package
                        break

                if not package:
                    return message('package not found')

            tests = [t for t in resources if t.startswith('Packages/%s/' % package)]

        if not len(tests):
            return message('ColorSchemeUnit: no tests found; be sure run tests from within the packages directory')

        if not output:
            output = TestOutputPanel('color_scheme_unit', self.window)

        output.write("ColorSchemeUnit %s\n\n" % __version__)
        output.write("Runtime: %s build %s\n" % (platform(), version()))
        output.write("Package: %s\n" % package)

        if file:
            output.write("File:    %s\n" % file)

        output.write("\n")

        result_printer = ResultPrinter(output, debug=self.view.settings().get('color_scheme_unit.debug'))
        code_coverage = Coverage(output, self.view.settings().get('color_scheme_unit.coverage'), file)

        skipped = []  # type: list
        errors = []  # type: list
        failures = []  # type: list
        total_assertions = 0

        result_printer.on_tests_start(tests)

        for i, test in enumerate(tests):
            test_result = run_color_scheme_test(test, self.window, result_printer, code_coverage)
            if test_result['error']:
                errors += [test_result['error']]
            if test_result['skip']:
                skipped += [test_result['skip']]
            failures += test_result['failures']
            total_assertions += test_result['assertions']

        result_printer.on_tests_end(errors, skipped, failures, total_assertions)

        if not errors and not failures:
            code_coverage.on_tests_end()

        if unittesting and is_async:
            if errors or failures:
                output.write('\n')
                output.write("FAILED.\n")
            else:
                output.write('\n')
                output.write("OK.\n")

            output.write('\n')
            output.write("UnitTesting: Done.\n")
            output.close()

        return not (errors or failures)
