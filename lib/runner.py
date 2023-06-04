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

_color_test_assertion = re.compile(
    '^\\s*(//|#|\\/\\*|\\<\\!--|--)\\s*'
    '(?P<repeat>\\^+)\\s+'
    '(?P<assertions>.+)'
    '$')

_color_test_assertion_fg = re.compile('fg=([^ ]+)')
_color_test_assertion_bg = re.compile('bg=([^ ]+)')
_color_test_assertion_fs = re.compile('fs=([a-z_]+ ?(?:[a-z_]+(?:$| ))*)')
_color_test_assertion_build = re.compile('build\\>=([0-9]+)')


def message(msg):
    msg = 'ColorSchemeUnit: {}'.format(msg)
    status_message(msg)
    print(msg)


def _parse_assertion(line: str):
    line = line.lower().rstrip(' -->').rstrip(' */')
    match = _color_test_assertion.match(line)

    if match:
        assertion = {
            'assertion': match.group(0),
            'repeat': match.group('repeat')
        }

        fg = _color_test_assertion_fg.search(match.group('assertions'))
        assertion['fg'] = fg.group(1) if fg else None

        bg = _color_test_assertion_bg.search(match.group('assertions'))
        assertion['bg'] = bg.group(1) if bg else None

        fs = _color_test_assertion_fs.search(match.group('assertions'))
        assertion['fs'] = fs.group(1).strip() if fs else None

        build = _color_test_assertion_build.search(match.group('assertions'))
        assertion['build'] = build.group(1) if build else None

        return assertion


def is_valid_color_scheme_test_file_name(file_name):
    if not file_name:
        return False

    return bool(re.match('^color_scheme_test.*\\.[a-zA-Z0-9-]+$', os.path.basename(file_name)))


def get_color_scheme_test_params_from_view(view):
    return get_color_scheme_test_params(view.substr(Region(0, view.size())))


def get_color_scheme_test_params(content: str, file_name=None):
    test_params = _color_test_params_compiled_pattern.match(content)
    if test_params:
        syntax_name = test_params.group('syntax_name')
        skip_if_not_syntax = test_params.group('skip_if_not_syntax')

        if test_params.group('color_scheme').endswith('.sublime-color-scheme'):
            color_scheme = test_params.group('color_scheme')
            if '/' in color_scheme and not color_scheme.startswith('Packages'):
                color_scheme = 'Packages/' + color_scheme
        else:
            color_scheme = 'Packages/' + test_params.group('color_scheme')

        syntax_package_name = None
        if not syntax_name and file_name is not None:
            syntax_name = os.path.splitext(file_name)[1].lstrip('.').upper()
        elif '/' in syntax_name:
            syntax_package_name, syntax_name = syntax_name.split('/')

        syntaxes = find_resources(syntax_name + '.sublime-syntax')
        if not syntaxes:
            syntaxes = find_resources(syntax_name + '.tmLanguage')
            if not syntaxes:
                syntaxes = find_resources(syntax_name + '.hidden-tmLanguage')

        if syntax_package_name:
            syntaxes = [s for s in syntaxes if syntax_package_name in s]

        return {
            'syntaxes': syntaxes,
            'syntax': syntaxes[0] if syntaxes else None,
            'syntax_name': syntax_name,
            'skip_if_not_syntax': bool(skip_if_not_syntax),
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
        test_params = get_color_scheme_test_params(test_content, test)

        if not test_params:
            err_msg = 'Invalid COLOR SCHEME TEST header'
            error['message'] = err_msg
            error['file'] = test_view.file_name()
            error['row'] = 0
            error['col'] = 0
            raise RuntimeError(err_msg)

        if len(test_params['syntaxes']) > 1:
            err_msg = 'More than one syntax found: {}'.format(test_params['syntaxes'])
            error['message'] = err_msg
            error['file'] = test_view.file_name()
            error['row'] = 0
            error['col'] = 0
            raise RuntimeError(err_msg)

        if len(test_params['syntaxes']) != 1:
            if test_params['skip_if_not_syntax']:
                err_msg = 'Syntax not found: {}'.format(test_params['syntax_name'])
                skip['message'] = err_msg
                skip['file'] = test_view.file_name()
                skip['row'] = 0
                skip['col'] = 0
                raise RuntimeError(err_msg)
            else:
                err_msg = 'Syntax not found: {}'.format(test_params['syntax_name'])
                error['message'] = err_msg
                error['file'] = test_view.file_name()
                error['row'] = 0
                error['col'] = 0
                raise RuntimeError(err_msg)

        test_view.view.assign_syntax(test_params['syntax'])
        test_view.view.settings().set('color_scheme', test_params['color_scheme'])
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
            assertion_params = _parse_assertion(line)
            if not assertion_params:
                consecutive_test_lines = 0
                continue

            consecutive_test_lines += 1

            requires_build = assertion_params['build']
            if requires_build:
                if int(version()) < int(requires_build):
                    continue

            assertion_row = line_number - consecutive_test_lines
            assertion_begin = line.find('^')
            assertion_repeat = assertion_params['repeat']
            assertion_end = assertion_begin + len(assertion_repeat)
            assertion_fg = assertion_params['fg']
            assertion_bg = assertion_params['bg']
            assertion_fs = assertion_params['fs']

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
                        'assertion': assertion_params['assertion'],
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
