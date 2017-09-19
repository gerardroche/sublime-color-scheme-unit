from unittest import TestCase

from color_scheme_unit.plugin import _COLOR_TEST_ASSERTION_COMPILED_PATTERN as pattern


class TestColorTestAssertionParamsPattern(TestCase):

    def assertMatch(self, string, expected):
        match = pattern.match(string)

        self.assertTrue(match)

        if 'repeat' not in expected:
            expected['repeat'] = None

        if 'fg' not in expected:
            expected['fg'] = None

        if 'bg' not in expected:
            expected['bg'] = None

        if 'fs' not in expected:
            expected['fs'] = None

        if 'build' not in expected:
            expected['build'] = None

        self.assertEquals(expected['repeat'], match.group('repeat'))
        self.assertEquals(expected['fg'], match.group('fg'))
        self.assertEquals(expected['bg'], match.group('bg'))
        self.assertEquals(expected['fs'], match.group('fs'))
        self.assertEquals(expected['build'], match.group('build'))

    def test_invalid(self):
        self.assertIsNone(pattern.match(''))
        self.assertIsNone(pattern.match('foo'))
        self.assertIsNone(pattern.match('// '))
        self.assertIsNone(pattern.match('// foo'))
        self.assertIsNone(pattern.match('// ^ ^'))
        self.assertIsNone(pattern.match('// ^^^ ^'))
        self.assertIsNone(pattern.match('// ^ foo'))
        self.assertIsNone(pattern.match('// ^ x=y'))

    def test_fg(self):
        self.assertMatch('// ^ fg=#ffffff', {'repeat': '^', 'fg': '#ffffff'})

    def test_bg(self):
        self.assertMatch('// ^ bg=#000000', {'repeat': '^', 'bg': '#000000'})

    def test_fs_italic(self):
        self.assertMatch('// ^ fs=italic', {'repeat': '^', 'fs': 'italic'})

    def test_fs_bold(self):
        self.assertMatch('// ^ fs=bold', {'repeat': '^', 'fs': 'bold'})

    def test_fs_bold_italic(self):
        self.assertMatch('// ^ fs=bold italic', {'repeat': '^', 'fs': 'bold italic'})

    def test_fg_build(self):
        self.assertMatch('// ^ fg=#ffffff build>=3127', {'repeat': '^', 'fg': '#ffffff', 'build': '3127'})

    def test_bg_build(self):
        self.assertMatch('// ^ bg=#000000 build>=3143', {'repeat': '^', 'bg': '#000000', 'build': '3143'})

    def test_fg_bg(self):
        self.assertMatch('// ^ fg=#ffffff bg=#000000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000'})

    def test_fg_bg_fs(self):
        self.assertMatch('// ^ fg=#ffffff bg=#000000 fs=bold', {
            'repeat': '^',
            'fg': '#ffffff',
            'bg': '#000000',
            'fs': 'bold'
        })

    def test_fg_bg_fs_build(self):
        self.assertMatch('// ^ fg=#ffffff bg=#000000 fs=italic bold underline build>=3133', {
            'repeat': '^',
            'fg': '#ffffff',
            'bg': '#000000',
            'fs': 'italic bold underline',
            'build': '3133'
        })

    def test_repeats(self):
        self.assertMatch('// ^^ fg=#ffffff', {'repeat': '^^', 'fg': '#ffffff'})
        self.assertMatch('// ^^^^^^^ bg=#000000', {'repeat': '^^^^^^^', 'bg': '#000000'})
        self.assertMatch('// ^^^ fg=#ffffff bg=#000000', {'repeat': '^^^', 'fg': '#ffffff', 'bg': '#000000'})

    def test_valid_comment_markers(self):
        comments = [  # start_comment, end_comment
            ['// ', ''],
            ['//', ''],
            ['# ', ''],
            ['/* ', ''],
            ['-- ', ''],
            ['<!-- ', ''],
        ]

        for start_comment, end_comment in comments:
            self.assertMatch(start_comment + '^ fg=#ffffff' + end_comment, {
                'repeat': '^',
                'fg': '#ffffff'
            })
