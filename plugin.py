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

__version__ = "1.4.1"
__version_info__ = (1, 4, 1)

_COLOR_TEST_PARAMS_COMPILED_PATTERN = re.compile(
    '^(?:(?:\<\?php )?(?://|#|\/\*|\<\!--)\s*)?'
    'COLOR SCHEME TEST "(?P<color_scheme>[^"]+)" "(?P<syntax_name>[^"]+)"'
    '(?:\s*(?:--\>|\?\>|\*\/))?')

_COLOR_TEST_ASSERTION_COMPILED_PATTERN = re.compile(
    '^\s*(//|#|\/\*|\<\!--)\s*'
    '(?P<repeat>\^+)'
    '(?: fg=(?P<fg>[^ ]+)?)?'
    '(?: bg=(?P<bg>[^ ]+)?)?'
    '(?: fs=(?P<fs>[^=]*)?)?'
    '$')


class TestView():

    def __init__(self, window, name):
        self.window = window
        self.name = name + '_test_view'

    def setUp(self):
        self.view = self.window.create_output_panel(
            self.name,
            unlisted=True
        )

    def tearDown(self):
        if self.view:
            self.view.close()

    def set_content(self, content):
        self.view.run_command('color_scheme_unit_setup_test_fixture', {
            'content': content
        })

    def get_content(self):
        return self.view.substr(Region(0, self.view.size()))


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

        view = window.active_view()
        if view:
            color_scheme = view.settings().get('color_scheme')
            if color_scheme:
                settings.set('color_scheme', color_scheme)

        window.run_command('show_panel', {
            'panel': 'output.' + name
        })

    def write(self, text):
        self.view.run_command('append', {
            'characters': text,
            'scroll_to_end': True
        })


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
        if self.debug:
            self.output.write('Starting %d test(s):\n' % len(tests))
            for test in tests:
                self.output.write('  \'%s\'\n' % test)

    def on_tests_end(self, errors, failures, total_assertions):
        self.output.write('\n\n')
        self.output.write('Time: %.2f secs\n' % (timer() - self.start_time))
        self.output.write('\n')

        if len(errors) > 0:
            self.output.write("There %s %s errors%s:\n\n" % (
                'was' if len(errors) == 1 else 'were',
                len(errors),
                '' if len(errors) == 1 else 's',
            ))
            self.output.write("\n")
            for i, error in enumerate(errors, start=1):
                self.output.write("%d) %s\n" % (i, error['message']))
                self.output.write("%s:%d:%d\n" % (error['file'], error['row'], error['col']))
                self.output.write("\n")

        if len(failures) > 0:
            self.output.write("There %s %s failure%s:\n\n" % (
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

        if len(errors) == 0 and len(failures) == 0:
            self.output.write("OK (%d tests, %d assertions)\n" % (self.tests, total_assertions))
        else:
            self.output.write("FAILURES!\n")
            self.output.write("Tests: %d, Assertions: %d" % (self.tests, total_assertions))
            if len(errors) > 0:
                self.output.write(", Errors: %d" % (len(errors)))
            self.output.write(", Failures: %d" % (len(failures)))
            self.output.write(".")
            self.output.write("\n")

    def on_test_start(self, test, data):
        if self.debug:
            self.output.write('\n\nStarting test \'{}\'\n  color scheme: \'{}\'\n  syntax: \'{}\'\n'
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
        self._wrap_progress()


class CodeCoverage():

    def __init__(self, output, enabled):
        self.output = output
        self.tests_info = {}
        self.enabled = enabled

    def on_test_start(self, test, info):
        self.tests_info[test] = info

    def on_tests_end(self):
        if not self.enabled:
            return

        self.output.write('\n')
        self.output.write('Generating code coverage report ...\n\n')

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
            'support',
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

                if 'settings' in struct:
                    if 'foreground' in struct['settings']:
                        colors.add(struct['settings']['foreground'].lower())

                    if 'background' in struct['settings']:
                        colors.add(struct['settings']['background'].lower())

                    if 'fontStyle' in struct['settings']:
                        if struct['settings']['fontStyle']:
                            styles.add(struct['settings']['fontStyle'].lower())

            report_data.append({
                'color_scheme': color_scheme,
                'syntaxes': syntaxes,
                'default_syntaxes': syntaxes & set(default_syntaxes),
                'minimal_syntaxes': syntaxes & set(minimal_syntaxes),
                'colors': colors,
                'scopes': scopes,
                'minimal_scopes': scopes & set(minimal_scopes),
                'styles': styles
            })

        cs_col_w = max([len(x['color_scheme']) for x in report_data])
        template = '{: <' + str(cs_col_w) + '} {: >12} {: >8} {: >14} {: >7}\n'

        self.output.write(template.format('Name', '', 'Syntaxes', 'Scopes', 'Colors'))
        self.output.write(('-' * cs_col_w) + '---------------------------------------------\n')
        for info in sorted(report_data, key=lambda x: x['color_scheme']):
            self.output.write(template.format(
                info['color_scheme'],
                '{} ({}/{})'.format(len(info['syntaxes']), len(info['minimal_syntaxes']), len(minimal_syntaxes)),
                '({}/{})'.format(len(info['default_syntaxes']), len(default_syntaxes)),
                '{} ({}/{})'.format(len(info['scopes']), len(info['minimal_scopes']), len(minimal_scopes)),
                len(info['colors']),
            ))

        self.output.write('\n')

        for i, info in enumerate(sorted(report_data, key=lambda x: x['color_scheme']), start=1):
            self.output.write('{}) {}\n\n'.format(i, info['color_scheme']))
            self.output.write('   Colors ({}) {}\n'.format(len(info['colors']), sorted(info['colors'])))
            self.output.write('   Styles ({}) {}\n'.format(len(info['styles']), sorted(info['styles'])))
            self.output.write('   Syntaxes ({}) {}\n'.format(len(info['syntaxes']), sorted(info['syntaxes'])))
            self.output.write('   Scopes ({}) {}\n'.format(len(info['scopes']), sorted(info['scopes'])))

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
                    self.output.write('   Minimal syntaxes not covered ({}):\n\n'.format(len(syntaxes_not_covered)))
                    for i, syntax in enumerate(syntaxes_not_covered, start=1):
                        self.output.write('   * {}\n'.format(syntax))

                if scopes_not_covered:
                    self.output.write('\n')
                    self.output.write('   Minimal scopes not covered ({}):\n\n'.format(len(scopes_not_covered)))
                    for i, scope in enumerate(scopes_not_covered, start=1):
                        self.output.write('   * {}\n'.format(scope))

            self.output.write('\n')

        self.output.write('\n')


def run_color_scheme_test(test, window, result_printer, code_coverage):
    error = False
    failures = []
    assertion_count = 0

    test_view = TestView(window, 'color_scheme_unit')
    test_view.setUp()

    try:
        test_content = load_resource(test)

        color_test_params = _COLOR_TEST_PARAMS_COMPILED_PATTERN.match(test_content)
        if not color_test_params:
            error = {
                'message': 'Invalid color scheme test: unable to find valid COLOR SCHEME TEST marker',
                'file': os.path.join(os.path.dirname(packages_path()), test),
                'row': 0,
                'col': 0
            }
            raise RuntimeError(error['message'])

        syntaxes = find_resources(color_test_params.group('syntax_name') + '.sublime-syntax')
        if len(syntaxes) > 1:
            error = {
                'message': 'Too many syntaxes found',
                'file': os.path.join(os.path.dirname(packages_path()), test),
                'row': 0,
                'col': 0
            }
            raise RuntimeError(error['message'])
        if len(syntaxes) is not 1:
            error = {
                'message': 'Syntaxes not found',
                'file': os.path.join(os.path.dirname(packages_path()), test),
                'row': 0,
                'col': 0
            }
            raise RuntimeError(error['message'])

        color_scheme = 'Packages/' + color_test_params.group('color_scheme')
        syntax = syntaxes[0]

        # This is down here rather than at the start of the function so that the
        # on_test_start method will have extra information like the color
        # scheme and syntax to print out if debugging is enabled.
        result_printer.on_test_start(test, {'color_scheme': color_scheme, 'syntax': syntax})
        code_coverage.on_test_start(test, {'color_scheme': color_scheme, 'syntax': syntax})

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
                        'file': os.path.join(os.path.dirname(packages_path()), test),
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
            file = os.path.realpath(file)
            if is_valid_color_scheme_test_file_name(file):
                self.run(file=file)
            else:
                return status_message('ColorSchemeUnit: file name not a valid test file name')
        else:
            return status_message('ColorSchemeUnit: file not found')

    def results(self):
        self.window.run_command('show_panel', {'panel': 'output.color_scheme_unit'})

    def run(self, file=None):
        set_timeout_async(lambda: self._run(file))

    def _run(self, test_file):
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

        output = TestOutputPanel('color_scheme_unit', self.window)
        output.write("ColorSchemeUnit %s\n\n" % __version__)
        output.write("Runtime: %s build %s\n" % (platform(), version()))
        output.write("Package: %s\n" % tests_package_name)
        if test_file:
            output.write("File:    %s\n" % test_file)

        output.write("\n")

        result_printer = ResultPrinter(output, debug=self.view.settings().get('color_scheme_unit.debug'))
        code_coverage = CodeCoverage(output, self.view.settings().get('color_scheme_unit.coverage'))

        errors = []
        failures = []
        total_assertions = 0

        result_printer.on_tests_start(tests)

        for i, test in enumerate(tests):
            test_result = run_color_scheme_test(test, self.window, result_printer, code_coverage)
            if test_result['error']:
                errors += [test_result['error']]
            failures += test_result['failures']
            total_assertions += test_result['assertions']

        result_printer.on_tests_end(errors, failures, total_assertions)

        if not errors and not failures:
            code_coverage.on_tests_end()


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
                    view.substr(Region(0, view.size())))

                if color_scheme_params:
                    color_scheme = 'Packages/' + color_scheme_params.group('color_scheme')
                    view.settings().set('color_scheme', color_scheme)
                    print('ColorSchemeUnit: applied color scheme \'{}\' to test view=[file=\'{}\''
                          .format(color_scheme, file_name))


class ColorSchemeUnitSetupTestFixtureCommand(TextCommand):

    def run(self, edit, content):
        self.view.erase(edit, Region(0, self.view.size()))
        self.view.insert(edit, 0, content)


class ColorSchemeUnitTestSuiteCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run()


class ColorSchemeUnitTestFileCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).run_file()


class ColorSchemeUnitTestResultsCommand(WindowCommand):

    def run(self):
        ColorSchemeUnit(self.window).results()
