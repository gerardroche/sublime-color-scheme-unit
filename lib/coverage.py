from ColorSchemeUnit.lib.color_scheme import is_new_scheme
from ColorSchemeUnit.lib.color_scheme import load_color_scheme_resource


_MINIMAL_SYNTAXES = [

    'Packages/C++/C.sublime-syntax',
    'Packages/CSS/CSS.sublime-syntax',
    'Packages/HTML/HTML.sublime-syntax',
    'Packages/JSON/JSON.sublime-syntax',
    'Packages/JavaScript/JavaScript.sublime-syntax',
    'Packages/Markdown/Markdown.sublime-syntax',
    'Packages/PHP/PHP.sublime-syntax',
    'Packages/Python/Python.sublime-syntax',
    'Packages/Ruby/Ruby.sublime-syntax',
    'Packages/XML/XML.sublime-syntax',

]

_MINIMAL_SCOPES = [

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
    'invalid.deprecated',
    'keyword',
    'keyword.control',
    'keyword.declaration',
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


class Coverage():

    def __init__(self, output, enabled, is_single_file):
        self.output = output
        self.enabled = enabled
        self.is_single_file = is_single_file
        self.tests_info = {}

    def on_test_start(self, test, data):
        if not self.enabled:
            return

        settings = data.settings()
        color_scheme = settings.get('color_scheme')
        syntax = settings.get('syntax')
        self.tests_info[test] = {
            'color_scheme': color_scheme,
            'syntax': syntax
        }

    def print(self, msg: str) -> None:
        self.output.write(msg)

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

        self.print('\n')
        self.print('Generating code coverage report...\n')
        self.print('\n')

        report_data = []
        for color_scheme, syntaxes in cs_tested_syntaxes.items():
            color_scheme_content = load_color_scheme_resource(color_scheme)
            syntaxes = set(syntaxes)

            if is_new_scheme(color_scheme):
                colors, scopes = _extract_new_scheme_info(color_scheme_content)
            else:
                colors, scopes = _extract_old_scheme_info(color_scheme_content)

            report_data.append({
                'color_scheme': color_scheme,
                'syntaxes': syntaxes,
                'minimal_syntaxes': set(_MINIMAL_SYNTAXES) & syntaxes,
                'colors': colors,
                'scopes': scopes,
                'minimal_scopes': set(_MINIMAL_SCOPES) & scopes,
            })

            tpl_col_width = max([len(x['color_scheme']) for x in report_data])
            tpl = '{: <' + str(tpl_col_width) + '} {: >20} {: >20}\n'

            self.print(tpl.format('Name', 'Minimal syntaxes', 'Minimal scopes'))
            self.print(('-' * tpl_col_width) + '------------------------------------------\n')
            for info in sorted(report_data, key=lambda x: x['color_scheme']):
                self.print(tpl.format(
                    info['color_scheme'],
                    '{} / {}'.format(len(info['minimal_syntaxes']), len(_MINIMAL_SYNTAXES)),
                    '{} / {}'.format(len(info['minimal_scopes']), len(_MINIMAL_SCOPES))))

            self.print('\n')

        for i, info in enumerate(sorted(report_data, key=lambda x: x['color_scheme']), start=1):
            self.print('{}) {}\n'.format(i, info['color_scheme']))

            syntaxes_not_covered = [s for s in sorted(_MINIMAL_SYNTAXES) if s not in info['syntaxes']]
            scopes_not_covered = [s for s in sorted(_MINIMAL_SCOPES) if s not in info['scopes']]
            notice_count = len(scopes_not_covered)
            if not self.is_single_file:
                notice_count += len(syntaxes_not_covered)

            if notice_count:
                self.print('\n')
                self.print('   There %s %s notice%s:' % (
                    'is' if notice_count == 1 else 'are',
                    notice_count,
                    '' if notice_count == 1 else 's',
                ))
                self.print('\n')

                # Minimal syntaxes tested report
                if syntaxes_not_covered and not self.is_single_file:
                    self.print('\n')
                    self.print('   The following is a recommended minimal set of syntaxes that should be tested.\n\n')
                    for i, syntax in enumerate(syntaxes_not_covered, start=1):
                        self.print('   {}/{}: {}\n'.format(i, len(syntaxes_not_covered), syntax))

                # Minimal scopes tested report
                if scopes_not_covered:
                    self.print('\n')
                    self.print('   The following is a recommended minimal set of scopes that your color scheme should support.\n')  # noqa: E501
                    self.print('   See https://www.sublimetext.com/docs/scope_naming.html#minimal-scope-coverage\n\n')
                    for i, scope in enumerate(scopes_not_covered, start=1):
                        self.print('   {}/{}: {}\n'.format(i, len(scopes_not_covered), scope))

            syntaxes_tested = sorted(info['syntaxes'])
            colors_used = sorted(info['colors'])
            colors_used_excl_alpha = sorted(set([color[0:7] for color in colors_used]))
            colors_used_incl_alpha = sorted(set([color for color in colors_used if len(color) > 7]))
            scopes_used = sorted(info['scopes'])

            tpl = '   {: <18} | {:>3} | {}\n'

            self.print('\n')
            self.print(tpl.format('Syntaxes tested', len(syntaxes_tested), sorted(syntaxes_tested)))
            self.print(tpl.format('Colors used', len(colors_used), colors_used))

            if len(colors_used_excl_alpha) != len(colors_used):
                self.print(tpl.format('Colors excl. alpha', len(colors_used_excl_alpha), colors_used_excl_alpha))

            if len(colors_used_incl_alpha):
                self.print(tpl.format('Colors incl. alpha', len(colors_used_incl_alpha), colors_used_incl_alpha))

            self.print(tpl.format('Scopes used', len(scopes_used), sorted(scopes_used)))
            self.print('\n')

        self.print('\n')


def _extract_new_scheme_info(content: dict) -> tuple:
    colors = set()

    if 'globals' in content:
        for k, v in content['globals'].items():
            if v.startswith('#'):
                colors.add(v.lower())
    if 'variables' in content:
        for k, v in content['variables'].items():
            if v.startswith('#'):
                colors.add(v.lower())
    if 'rules' in content:
        for rule in content['rules']:
            for k, v in rule.items():
                if v.startswith('#'):
                    colors.add(v.lower())

    scopes = set()

    if 'rules' in content:
        for rule in content['rules']:
            for scope in rule['scope'].split(','):
                scopes.add(scope.strip())

    return (colors, scopes)


def _extract_old_scheme_info(content: dict) -> tuple:
    colors = set()
    scopes = set()

    for struct in content['settings']:
        if 'scope' in struct:
            for scope in struct['scope'].split(','):
                scopes.add(scope.strip())
        else:
            if 'settings' in struct:
                for k, v in struct['settings'].items():
                    if v.startswith('#'):
                        colors.add(v.lower())

        if 'settings' in struct:
            if 'foreground' in struct['settings']:
                colors.add(struct['settings']['foreground'].lower())

            if 'background' in struct['settings']:
                colors.add(struct['settings']['background'].lower())

    return (colors, scopes)
