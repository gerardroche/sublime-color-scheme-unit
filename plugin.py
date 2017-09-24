import os
import re
import plistlib
from timeit import default_timer as timer

from sublime import find_resources
from sublime import load_resource
from sublime import packages_path
from sublime import platform
from sublime import Region
from sublime import score_selector
from sublime import set_clipboard
from sublime import set_timeout_async
from sublime import status_message
from sublime import version
from sublime_plugin import EventListener
from sublime_plugin import TextCommand
from sublime_plugin import WindowCommand

__version__ = "1.7.0"
__version_info__ = (1, 7, 0)

_COLOR_TEST_PARAMS_COMPILED_PATTERN = re.compile(
    '^(?:(?:\<\?php )?(?://|#|\/\*|\<\!--|--)\s*)?'
    'COLOR SCHEME TEST "(?P<color_scheme>[^"]+)"(?:(?P<skip_if_not_syntax> SKIP IF NOT)? "(?P<syntax_name>[^"]+)")?'
    '(?:\s*(?:--\>|\?\>|\*\/))?')

_COLOR_TEST_ASSERTION_COMPILED_PATTERN = re.compile(
    '^\s*(//|#|\/\*|\<\!--|--)\s*'
    '(?P<repeat>\^+)'
    '(?: fg=(?P<fg>[^ ]+)?)?'
    '(?: bg=(?P<bg>[^ ]+)?)?'
    '(?: fs=(?P<fs>[^=]*)?)?'
    '(?: build\\>=(?P<build>[^=]*)?)?'
    '$')

_PACKAGE_NAME = __name__.split('.')[0]


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
        self.view.run_command('color_scheme_unit_setup_test_fixture', {
            'content': content
        })

    def get_content(self):
        return self.view.substr(Region(0, self.view.size()))


class TestOutputPanel():

    def __init__(self, name, window):
        self.window = window
        self.name = name
        self.view = window.create_output_panel(name)

        settings = self.view.settings()
        settings.set('result_file_regex', '^(.+):([0-9]+):([0-9]+)$')
        settings.set('word_wrap', False)
        settings.set('line_numbers', False)
        settings.set('gutter', False)
        settings.set('rulers', [])
        settings.set('scroll_past_end', False)

        if int(version()) > 3083:
            self.view.assign_syntax('Packages/' + _PACKAGE_NAME + '/res/text-ui-result.sublime-syntax')

        view = window.active_view()
        if view:
            color_scheme = view.settings().get('color_scheme')
            if color_scheme:
                settings.set('color_scheme', color_scheme)

        self.show()

        self.closed = False

    def write(self, text):
        self.view.run_command('append', {
            'characters': text,
            'scroll_to_end': True
        })

    def writeln(self, s):
        self.write(s + "\n")

    def flush(self):
        pass

    def show(self):
        self.window.run_command("show_panel", {"panel": "output." + self.name})

    def close(self):
        self.closed = True


class ColorSchemeStyle():

    def __init__(self, view):
        self._view = view
        self._scope_style_cache = {}

        color_scheme = self._view.settings().get('color_scheme')
        self._plist = plistlib.readPlistFromBytes(bytes(load_resource(color_scheme), 'UTF-8'))

        self._default_styles = {}
        for plist_settings_dict in self._plist['settings']:
            if 'scope' not in plist_settings_dict:
                self._default_styles.update(plist_settings_dict['settings'])

    def at_point(self, point):
        scope = self._view.scope_name(point).strip()

        if scope in self._scope_style_cache:
            return self._scope_style_cache[scope]

        style = self._default_styles.copy()
        scored_styles = []
        for color_scheme_definition in self._plist['settings']:
            if 'scope' in color_scheme_definition:
                score = score_selector(scope, color_scheme_definition['scope'])
                if score:
                    color_scheme_definition.update({'score': score})
                    scored_styles.append(color_scheme_definition)

        for s in sorted(scored_styles, key=lambda k: k['score']):
            style.update(s['settings'])

        self._scope_style_cache[scope] = style

        return style


class ResultPrinter():

    def __init__(self, output, debug=False):
        self.assertions = 0
        self.tests = 0
        self.tests_total = 0
        self.output = output
        self.debug = debug
        self._progress_count = 0

    def on_tests_start(self, tests):
        self.tests_total = len(tests)
        self.start_time = timer()
        if self.debug:
            self.output.write('Starting {} test{}:\n\n'.format(
                len(tests),
                's' if len(tests) > 1 else ''
            ))

            for i, test in enumerate(tests, start=1):
                self.output.write('%d) %s\n' % (i, test))

    def on_tests_end(self, errors, skipped, failures, total_assertions):
        self.output.write('\n\n')
        self.output.write('Time: %.2f secs\n' % (timer() - self.start_time))
        self.output.write('\n')

        # ERRORS
        if len(errors) > 0:
            self.output.write("There %s %s error%s:\n" % (
                'was' if len(errors) == 1 else 'were',
                len(errors),
                '' if len(errors) == 1 else 's',
            ))
            self.output.write("\n")
            for i, error in enumerate(errors, start=1):
                self.output.write("%d) %s\n" % (i, error['message']))
                self.output.write("\n%s:%d:%d\n" % (error['file'], error['row'], error['col']))
                self.output.write("\n")

        # FAILURES
        if len(failures) > 0:
            if len(errors) > 0:
                self.output.write("--\n\n")

            self.output.write("There %s %s failure%s:\n" % (
                'was' if len(failures) == 1 else 'were',
                len(failures),
                '' if len(failures) == 1 else 's',
            ))

            for i, failure in enumerate(failures, start=1):
                self.output.write("%d) %s\n" % (i, failure['assertion']))
                self.output.write("Failed asserting %s equals %s\n" % (
                    str(failure['actual']), str(failure['expected'])))
                # TODO failure diff
                # self.output.write("--- Expected\n")
                # self.output.write("+++ Actual\n")
                # self.output.write("@@ @@\n")
                # self.output.write("{{diff}}\n\n")
                self.output.write("%s:%d:%d\n" % (failure['file'], failure['row'], failure['col']))
                self.output.write("\n")

        # SKIPPED
        if len(skipped) > 0:
            if (len(errors) + len(failures)) > 0:
                self.output.write("--\n\n")

            self.output.write("There %s %s skipped test%s:\n" % (
                'was' if len(skipped) == 1 else 'were',
                len(skipped),
                '' if len(skipped) == 1 else 's',
            ))
            self.output.write("\n")
            for i, skip in enumerate(skipped, start=1):
                self.output.write("%d) %s\n" % (i, skip['message']))
                self.output.write("\n%s:%d:%d\n" % (skip['file'], skip['row'], skip['col']))
                self.output.write("\n")

        # TOTALS
        if len(errors) == 0 and len(failures) == 0:
            self.output.write("OK (%d tests, %d assertions" % (self.tests, total_assertions))
            if len(skipped) > 0:
                self.output.write(", %d skipped" % (len(skipped)))
            self.output.write(")\n")
        else:
            self.output.write("FAILURES!\n")
            self.output.write("Tests: %d, Assertions: %d" % (self.tests, total_assertions))
            if len(errors) > 0:
                self.output.write(", Errors: %d" % (len(errors)))
            self.output.write(", Failures: %d" % (len(failures)))
            if len(skipped) > 0:
                self.output.write(", Skipped: %d" % (len(skipped)))

            self.output.write(".")
            self.output.write("\n")

    def on_test_start(self, test, data):
        if self.debug:
            settings = data.settings()
            color_scheme = settings.get('color_scheme')
            syntax = settings.get('syntax')
            self.output.write('\nStarting test \'{}\'\n  color scheme: \'{}\'\n  syntax: \'{}\'\n'
                              .format(test, color_scheme, syntax))

    def _writeProgress(self, c):
        self.output.write(c)
        self._progress_count += 1
        if self._progress_count % 80 == 0:
            self.output.write(' %d / %s (%3.1f%%)\n' % (
                self.tests,
                self.tests_total,
                (self.tests / self.tests_total) * 100)
            )

    def on_test_end(self):
        self.tests += 1

    def addError(self, test, data):
        self._writeProgress('E')

    def addSkippedTest(self, test, data):
        if self.debug:
            settings = data.settings()
            color_scheme = settings.get('color_scheme')
            syntax = settings.get('syntax')
            self.output.write('\nSkipping test \'{}\'\n  color scheme: \'{}\'\n  syntax: \'{}\'\n'
                              .format(test, color_scheme, syntax))

        self._writeProgress('S')

    def on_assertion_success(self):
        self.assertions += 1
        self._writeProgress('.')

    def on_assertion_failure(self, failure_trace):
        self.assertions += 1
        self._writeProgress('F')


class CodeCoverage():

    def __init__(self, output, enabled):
        self.output = output
        self.tests_info = {}
        self.enabled = enabled

    def on_test_start(self, test, data):
        settings = data.settings()
        color_scheme = settings.get('color_scheme')
        syntax = settings.get('syntax')
        self.tests_info[test] = {
            'color_scheme': color_scheme,
            'syntax': syntax
        }

    def on_tests_end(self):
        if not self.enabled:
            return

        default_syntaxes = [
            'Packages/R/Rd (R Documentation).sublime-syntax',
            'Packages/R/R Console.sublime-syntax',
            'Packages/R/R.sublime-syntax',
            'Packages/ShellScript/Shell-Unix-Generic.sublime-syntax',
            'Packages/Groovy/Groovy.sublime-syntax',
            'Packages/Scala/Scala.sublime-syntax',
            'Packages/Ruby/Ruby.sublime-syntax',
            'Packages/Haskell/Haskell.sublime-syntax',
            'Packages/Haskell/Literate Haskell.sublime-syntax',
            'Packages/Textile/Textile.sublime-syntax',
            'Packages/Makefile/Make Output.sublime-syntax',
            'Packages/Makefile/Makefile.sublime-syntax',
            'Packages/C++/C.sublime-syntax',
            'Packages/C++/C++.sublime-syntax',
            'Packages/HTML/HTML.sublime-syntax',
            'Packages/Rails/HTML (Rails).sublime-syntax',
            'Packages/Rails/SQL (Rails).sublime-syntax',
            'Packages/Rails/Ruby on Rails.sublime-syntax',
            'Packages/Rails/Ruby Haml.sublime-syntax',
            'Packages/Rails/JavaScript (Rails).sublime-syntax',
            'Packages/Objective-C/Objective-C++.sublime-syntax',
            'Packages/Objective-C/Objective-C.sublime-syntax',
            'Packages/PHP/PHP.sublime-syntax',
            'Packages/PHP/PHP Source.sublime-syntax',
            'Packages/Markdown/MultiMarkdown.sublime-syntax',
            'Packages/Markdown/Markdown.sublime-syntax',
            'Packages/Graphviz/DOT.sublime-syntax',
            'Packages/ASP/HTML-ASP.sublime-syntax',
            'Packages/ASP/ASP.sublime-syntax',
            'Packages/LaTeX/LaTeX Log.sublime-syntax',
            'Packages/LaTeX/Bibtex.sublime-syntax',
            'Packages/LaTeX/LaTeX.sublime-syntax',
            'Packages/LaTeX/TeX.sublime-syntax',
            'Packages/JavaScript/Regular Expressions (JavaScript).sublime-syntax',
            'Packages/JavaScript/JSON.sublime-syntax',
            'Packages/JavaScript/JavaScript.sublime-syntax',
            'Packages/CSS/CSS.sublime-syntax',
            'Packages/Matlab/Matlab.sublime-syntax',
            'Packages/Rust/Cargo.sublime-syntax',
            'Packages/Rust/Rust.sublime-syntax',
            'Packages/Regular Expressions/RegExp.sublime-syntax',
            'Packages/XML/XML.sublime-syntax',
            'Packages/Lua/Lua.sublime-syntax',
            'Packages/AppleScript/AppleScript.sublime-syntax',
            'Packages/Java/Java.sublime-syntax',
            'Packages/Java/JavaProperties.sublime-syntax',
            'Packages/Java/JavaDoc.sublime-syntax',
            'Packages/Java/Java Server Pages (JSP).sublime-syntax',
            'Packages/ActionScript/ActionScript.sublime-syntax',
            'Packages/SQL/SQL.sublime-syntax',
            'Packages/Python/Python.sublime-syntax',
            'Packages/Python/Regular Expressions (Python).sublime-syntax',
            'Packages/OCaml/camlp4.sublime-syntax',
            'Packages/OCaml/OCamllex.sublime-syntax',
            'Packages/OCaml/OCaml.sublime-syntax',
            'Packages/OCaml/OCamlyacc.sublime-syntax',
            'Packages/Erlang/HTML (Erlang).sublime-syntax',
            'Packages/Erlang/Erlang.sublime-syntax',
            'Packages/Diff/Diff.sublime-syntax',
            'Packages/Go/Go.sublime-syntax',
            'Packages/Pascal/Pascal.sublime-syntax',
            'Packages/C#/Build.sublime-syntax',
            'Packages/C#/C#.sublime-syntax',
            'Packages/Perl/Perl.sublime-syntax',
            'Packages/D/D.sublime-syntax',
            'Packages/RestructuredText/reStructuredText.sublime-syntax',
            'Packages/TCL/HTML (Tcl).sublime-syntax',
            'Packages/TCL/Tcl.sublime-syntax',
            'Packages/YAML/YAML.sublime-syntax',
            'Packages/Batch File/Batch File.sublime-syntax',
            'Packages/Clojure/Clojure.sublime-syntax',
            'Packages/Lisp/Lisp.sublime-syntax',
        ]

        minimal_syntaxes = [
            'Packages/Ruby/Ruby.sublime-syntax',
            'Packages/C++/C.sublime-syntax',
            'Packages/HTML/HTML.sublime-syntax',
            'Packages/PHP/PHP.sublime-syntax',
            'Packages/Markdown/Markdown.sublime-syntax',
            'Packages/JavaScript/JSON.sublime-syntax',
            'Packages/JavaScript/JavaScript.sublime-syntax',
            'Packages/CSS/CSS.sublime-syntax',
            'Packages/XML/XML.sublime-syntax',
            'Packages/Python/Python.sublime-syntax',
        ]

        minimal_scopes = [
            'comment',
            'constant',
            'constant.character.escape',
            'constant.language',
            'constant.numeric',
            'entity.name',
            'entity.name.section',
            'entity.name.tag',
            'entity.other.attribute-name',
            'entity.other.inherited-class',
            'invalid',
            'keyword',
            'keyword.control',
            'keyword.operator',
            'storage.modifier',
            'storage.type',
            'string',
            'variable',
            'variable.function',
            'variable.language',
            'variable.parameter',
        ]

        cs_tested_syntaxes = {}
        for test, info in self.tests_info.items():
            cs = info['color_scheme']
            s = info['syntax']
            if cs not in cs_tested_syntaxes:
                cs_tested_syntaxes[cs] = []
            cs_tested_syntaxes[cs].append(s)

        if not cs_tested_syntaxes:
            return

        self.output.write('\n')
        self.output.write('Generating code coverage report ...\n\n')

        report_data = []
        for color_scheme, syntaxes in cs_tested_syntaxes.items():
            color_scheme_plist = plistlib.readPlistFromBytes(bytes(load_resource(color_scheme), 'UTF-8'))
            syntaxes = set(syntaxes)
            colors = set()
            scopes = set()
            styles = set()

            for struct in color_scheme_plist['settings']:
                if 'scope' in struct:
                    for scope in struct['scope'].split(','):
                        scopes.add(scope.strip())
                else:
                    if 'settings' in struct:
                        for k, v in struct['settings'].items():
                            if v.startswith('#'):
                                colors.add(v.lower())
                            else:
                                styles.add(v)

                if 'settings' in struct:
                    if 'foreground' in struct['settings']:
                        colors.add(struct['settings']['foreground'].lower())

                    if 'background' in struct['settings']:
                        colors.add(struct['settings']['background'].lower())

                    if 'fontStyle' in struct['settings']:
                        if struct['settings']['fontStyle']:
                            styles.add(struct['settings']['fontStyle'])

            report_data.append({
                'color_scheme': color_scheme,
                'syntaxes': syntaxes,
                'default_syntaxes': set(default_syntaxes) & syntaxes,
                'minimal_syntaxes': set(minimal_syntaxes) & syntaxes,
                'colors': colors,
                'scopes': scopes,
                'minimal_scopes': set(minimal_scopes) & scopes,
                'styles': styles
            })

        cs_col_w = max([len(x['color_scheme']) for x in report_data])
        template = '{: <' + str(cs_col_w) + '} {: >20} {: >20}\n'

        self.output.write(template.format('Name', 'Minimal Syntax Tests', 'Minimal Scopes'))
        self.output.write(('-' * cs_col_w) + '------------------------------------------\n')
        for info in sorted(report_data, key=lambda x: x['color_scheme']):
            self.output.write(template.format(
                info['color_scheme'],
                '{} / {}'.format(len(info['minimal_syntaxes']), len(minimal_syntaxes)),
                '{} / {}'.format(len(info['minimal_scopes']), len(minimal_scopes))
            ))

        self.output.write('\n')

        for i, info in enumerate(sorted(report_data, key=lambda x: x['color_scheme']), start=1):
            self.output.write('{}) {}\n'.format(i, info['color_scheme']))

            syntaxes_not_covered = [s for s in sorted(minimal_syntaxes) if s not in info['syntaxes']]
            scopes_not_covered = [s for s in sorted(minimal_scopes) if s not in info['scopes']]
            total_notice_count = len(syntaxes_not_covered) + len(scopes_not_covered)

            if total_notice_count:
                self.output.write('\n')
                self.output.write('   There %s %s notice%s:\n' % (
                    'is' if total_notice_count == 1 else 'are',
                    total_notice_count,
                    '' if total_notice_count == 1 else 's',
                ))

                if syntaxes_not_covered:
                    self.output.write('\n')
                    self.output.write('   Minimal syntaxes tests not covered ({}):\n\n'
                                      .format(len(syntaxes_not_covered)))
                    for i, syntax in enumerate(syntaxes_not_covered, start=1):
                        self.output.write('   * {}\n'.format(syntax))

                if scopes_not_covered:
                    self.output.write('\n')
                    self.output.write('   Minimal scopes not covered ({}):\n\n'.format(len(scopes_not_covered)))
                    for i, scope in enumerate(scopes_not_covered, start=1):
                        self.output.write('   * {}\n'.format(scope))

            self.output.write('\n')
            self.output.write('   Information:\n\n')
            self.output.write('   Colors   {: >3} {}\n'.format(len(info['colors']), sorted(info['colors'])))
            self.output.write('   Styles   {: >3} {}\n'.format(len(info['styles']), sorted(info['styles'])))
            self.output.write('   Syntaxes {: >3} {}\n'.format(len(info['syntaxes']), sorted(info['syntaxes'])))
            self.output.write('   Scopes   {: >3} {}\n'.format(len(info['scopes']), sorted(info['scopes'])))
            self.output.write('\n')

        self.output.write('\n')


def run_color_scheme_test(test, window, result_printer, code_coverage):
    skip = False
    error = False
    failures = []
    assertion_count = 0

    test_view = TestView(window, test)
    test_view.setUp()

    try:
        test_content = load_resource(test)

        color_test_params = _COLOR_TEST_PARAMS_COMPILED_PATTERN.match(test_content)
        if not color_test_params:
            error = {'message': 'Invalid COLOR SCHEME TEST header', 'file': test_view.file_name(), 'row': 0, 'col': 0}
            raise RuntimeError(error['message'])

        syntax = color_test_params.group('syntax_name')
        if not syntax:
            syntax = os.path.splitext(test)[1].lstrip('.').upper()

        syntaxes = find_resources(syntax + '.sublime-syntax')
        if not syntaxes:
            syntaxes = find_resources(syntax + '.tmLanguage')

        if len(syntaxes) > 1:
            error = {'message': 'More than one syntax found: {}'.format(syntaxes), 'file': test_view.file_name(), 'row': 0, 'col': 0}
            raise RuntimeError(error['message'])

        if len(syntaxes) != 1:
            if color_test_params.group('skip_if_not_syntax'):
                skip = {'message': 'Syntax not found: {}'.format(syntax), 'file': test_view.file_name(), 'row': 0, 'col': 0}
                raise RuntimeError(error['message'])
            else:
                error = {'message': 'Syntax not found: {}'.format(syntax), 'file': test_view.file_name(), 'row': 0, 'col': 0}
                raise RuntimeError(error['message'])

        test_view.view.assign_syntax(syntaxes[0])
        test_view.view.settings().set('color_scheme', 'Packages/' + color_test_params.group('color_scheme'))
        test_view.set_content(test_content)

        color_scheme_style = ColorSchemeStyle(test_view.view)

        # This is down here rather than at the start of the function so that the
        # on_test_start method will have extra information like the color
        # scheme and syntax to print out if debugging is enabled.
        result_printer.on_test_start(test, test_view)
        code_coverage.on_test_start(test, test_view)

        consecutive_test_lines = 0
        for line_number, line in enumerate(test_content.splitlines()):
            assertion_params = _COLOR_TEST_ASSERTION_COMPILED_PATTERN.match(line.lower().rstrip(' -->').rstrip(' */'))
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

                if actual == expected:
                    result_printer.on_assertion_success()
                else:
                    failure_trace = {
                        'assertion': assertion_params.group(0),
                        'file': test_view.file_name(),
                        'row': assertion_row + 1,
                        'col': col + 1,
                        'actual': actual,
                        'expected': expected,
                    }

                    result_printer.on_assertion_failure(failure_trace)

                    failures.append(failure_trace)

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
            file = os.path.realpath(file)
            if is_valid_color_scheme_test_file_name(file):
                self.run(file=file)
            else:
                return status_message('ColorSchemeUnit: file name not a valid test file name')
        else:
            return status_message('ColorSchemeUnit: file not found')

    def results(self):
        self.window.run_command('show_panel', {'panel': 'output.color_scheme_unit'})

    def run(self, file=None, output=None):
        set_timeout_async(lambda: self._run(file, output))

    def _run(self, test_file, output=None):
        unittesting = True if output else False

        file_name = self.view.file_name()
        if not file_name:
            return status_message('ColorSchemeUnit: file not found')

        file_name = os.path.realpath(file_name)

        def normalise_resource_path(path):
            if platform() == 'windows':
                path = re.sub(r"/", r"\\", path)

            return path

        tests = []
        resources = find_resources('color_scheme_test*')
        for resource in resources:
            package = resource.split('/')[1]
            package_path = os.path.join(packages_path(), package)
            if file_name.startswith(package_path):
                tests_package_name = package
                if test_file:
                    resource_file = os.path.join(
                        os.path.dirname(packages_path()),
                        normalise_resource_path(resource)
                    )
                    if test_file == resource_file:
                        tests.append(resource)
                else:
                    tests.append(resource)

        if not len(tests):
            print('ColorSchemeUnit: no test found')
            print('ColorSchemeUnit: make sure you are running tests from within the packages directory')

            return status_message(
                'ColorSchemeUnit: no tests found; be sure run tests from within the packages directory')

        if not output:
            output = TestOutputPanel('color_scheme_unit', self.window)
        output.write("ColorSchemeUnit %s\n\n" % __version__)
        output.write("Runtime: %s build %s\n" % (platform(), version()))
        output.write("Package: %s\n" % tests_package_name)
        if test_file:
            output.write("File:    %s\n" % test_file)

        output.write("\n")

        result_printer = ResultPrinter(output, debug=self.view.settings().get('color_scheme_unit.debug'))
        code_coverage = CodeCoverage(output, self.view.settings().get('color_scheme_unit.coverage'))

        skipped = []
        errors = []
        failures = []
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

        if unittesting:
            if errors or failures:
                output.write('\n')
                output.write("FAILED.\n")
            else:
                output.write('\n')
                output.write("OK.\n")

            output.write('\n')
            output.write("UnitTesting: Done.\n")
            output.close()


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


class ColorSchemeUnitSetColorSchemeOnLoadEvent(EventListener):

    def on_load_async(self, view):
        file_name = view.file_name()
        if file_name:
            if is_valid_color_scheme_test_file_name(file_name):
                color_scheme_params = _COLOR_TEST_PARAMS_COMPILED_PATTERN.match(
                    view.substr(Region(0, view.size()))
                )

                if color_scheme_params:
                    color_scheme = 'Packages/' + color_scheme_params.group('color_scheme')
                    view.settings().set('color_scheme', color_scheme)
                    print('ColorSchemeUnit: apply color scheme \'{}\' to view=[file=\'{}\''
                          .format(color_scheme, file_name))


class ColorSchemeUnitSetupTestFixtureCommand(TextCommand):

    def run(self, edit, content):
        self.view.erase(edit, Region(0, self.view.size()))
        self.view.insert(edit, 0, content)


def _generate_assertions(styles, comment_start, comment_end):
    line_styles_count = len(styles)
    repeat_count = 0
    indent_count = 0
    prev_style = None
    assertions = []
    for i, style in enumerate(styles):
        if style == prev_style:
            repeat_count += 1
        else:
            if prev_style is not None:
                assertions.append((indent_count * ' ') + ('^' * repeat_count) + ' ' + prev_style)
                indent_count += repeat_count
                repeat_count = 1
            else:
                repeat_count += 1
        prev_style = style
        if line_styles_count == i + 1:
            assertions.append((indent_count * ' ') + ('^' * repeat_count) + ' ' + prev_style)

    assertions_str = ''
    for assertion in assertions:
        assertion = assertion[len(comment_start):]
        if assertion.lstrip(' ').startswith('^') and assertion.strip(' ^') != '':
            assertions_str += comment_start + assertion + comment_end + '\n'

    return assertions_str.rstrip('\n')


def _get_comment_markers(view, pt):
    comment_start = ''
    comment_end = ''
    for v in view.meta_info('shellVariables', pt):
        if v['name'] == 'TM_COMMENT_START':
            comment_start = v['value']
            if not comment_start.endswith(' '):
                comment_start = comment_start + ' '

        if v['name'] == 'TM_COMMENT_END':
            comment_end = v['value']
            if not comment_end.startswith(' '):
                comment_end = ' ' + comment_end

    return (comment_start, comment_end)


class ColorSchemeUnitInsertAssertions(TextCommand):

    def run(self, edit):
        pt = self.view.sel()[0].begin()
        line = self.view.line(pt)

        styles = []
        color_scheme_style = ColorSchemeStyle(self.view)
        for i in range(line.begin(), line.end()):
            if self.view.substr(i) == ' ':
                styles.append('')
            else:
                style = color_scheme_style.at_point(i)
                if 'fontStyle' not in style:
                    style['fontStyle'] = ''

                styles.append('fg={} fs={}'.format(style['foreground'], style['fontStyle']))

        comment_start, comment_end = _get_comment_markers(self.view, pt)
        assertions = _generate_assertions(styles, comment_start, comment_end)

        self.view.insert(edit, line.end(), '\n' + assertions)


# TODO Should this helper be in its own package because it's useful for syntax devs?
class ColorSchemeUnitInsertScopes(TextCommand):

    def run(self, edit):
        pt = self.view.sel()[0].begin()
        line = self.view.line(pt)

        scopes = []
        for i in range(line.begin(), line.end()):
            scopes.append(self.view.scope_name(i).rstrip(' '))

        comment_start, comment_end = _get_comment_markers(self.view, pt)
        assertions = _generate_assertions(scopes, comment_start, comment_end)

        self.view.insert(edit, line.end(), '\n' + assertions)


class ColorSchemeUnitUnitTestingCommand(WindowCommand):
    def run(self, *args, **kwargs):
        output = kwargs.get('output')
        stream = open(output, "w")

        ColorSchemeUnit(self.window).run(output=stream)


class ColorSchemeUnitTestSuiteCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run()


class ColorSchemeUnitTestFileCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run_file()


class ColorSchemeUnitTestResultsCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).results()
