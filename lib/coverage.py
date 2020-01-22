from ColorSchemeUnit.lib.color_scheme import load_color_scheme_resource


_default_syntaxes = [
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

_minimal_syntaxes = [
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

_minimal_scopes = [
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


class Coverage():

    def __init__(self, output, enabled, is_single_file):
        self.output = output
        self.enabled = enabled
        self.is_single_file = is_single_file
        self.tests_info = {}

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

        cs_tested_syntaxes = {}  # type: dict
        for test, info in self.tests_info.items():
            cs = info['color_scheme']
            s = info['syntax']
            if cs not in cs_tested_syntaxes:
                cs_tested_syntaxes[cs] = []
            cs_tested_syntaxes[cs].append(s)

        if not cs_tested_syntaxes:
            return

        self.output.write('\n')
        self.output.write('Generating code coverage report...\n\n')

        report_data = []
        for color_scheme, syntaxes in cs_tested_syntaxes.items():
            color_scheme_plist = load_color_scheme_resource(color_scheme)
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
                'default_syntaxes': set(_default_syntaxes) & syntaxes,
                'minimal_syntaxes': set(_minimal_syntaxes) & syntaxes,
                'colors': colors,
                'scopes': scopes,
                'minimal_scopes': set(_minimal_scopes) & scopes,
                'styles': styles
            })

        cs_col_w = max([len(x['color_scheme']) for x in report_data])
        template = '{: <' + str(cs_col_w) + '} {: >20} {: >20}\n'

        self.output.write(template.format('Name', 'Minimal Syntax Tests', 'Minimal Scopes'))
        self.output.write(('-' * cs_col_w) + '------------------------------------------\n')
        for info in sorted(report_data, key=lambda x: x['color_scheme']):
            self.output.write(template.format(
                info['color_scheme'],
                '{} / {}'.format(len(info['minimal_syntaxes']), len(_minimal_syntaxes)),
                '{} / {}'.format(len(info['minimal_scopes']), len(_minimal_scopes))
            ))

        self.output.write('\n')

        for i, info in enumerate(sorted(report_data, key=lambda x: x['color_scheme']), start=1):
            self.output.write('{}) {}\n'.format(i, info['color_scheme']))

            syntaxes_not_covered = [s for s in sorted(_minimal_syntaxes) if s not in info['syntaxes']]
            scopes_not_covered = [s for s in sorted(_minimal_scopes) if s not in info['scopes']]
            total_notice_count = len(scopes_not_covered)
            if not self.is_single_file:
                total_notice_count += len(syntaxes_not_covered)

            if total_notice_count:
                self.output.write('\n')
                self.output.write('   There %s %s notice%s:\n' % (
                    'is' if total_notice_count == 1 else 'are',
                    total_notice_count,
                    '' if total_notice_count == 1 else 's',
                ))

                if syntaxes_not_covered and not self.is_single_file:
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

            self.output.write('   Colors   {: >3} {}\n'.format(len(info['colors']), sorted(info['colors'])))

            excluding_alpha = sorted(set([color[0:7] for color in info['colors']]))
            self.output.write('            {: >3} {}\n'.format(len(excluding_alpha), sorted(excluding_alpha)))

            including_alpha = sorted(set([color for color in info['colors'] if len(color) > 7]))
            self.output.write('            {: >3} {}\n'.format(len(including_alpha), sorted(including_alpha)))

            self.output.write('   Styles   {: >3} {}\n'.format(len(info['styles']), sorted(info['styles'])))
            self.output.write('   Syntaxes {: >3} {}\n'.format(len(info['syntaxes']), sorted(info['syntaxes'])))
            self.output.write('   Scopes   {: >3} {}\n'.format(len(info['scopes']), sorted(info['scopes'])))
            self.output.write('\n')

        self.output.write('\n')
