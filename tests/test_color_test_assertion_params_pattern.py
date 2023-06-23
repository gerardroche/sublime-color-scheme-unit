from unittest import TestCase

from ColorSchemeUnit.lib.runner import _parse_assertion


class TestColorTestAssertionParamsPattern(TestCase):

    def assertMatch(self, string, expected):
        defaults = {
            'repeat': None,
            'fg': None,
            'bg': None,
            'fs': None,
            'build': None
        }
        defaults.update(expected)
        expected = defaults

        match = _parse_assertion(string)

        self.assertTrue(match)
        self.assertEquals(expected['repeat'], match['repeat'])
        self.assertEquals(expected['fg'], match['fg'])
        self.assertEquals(expected['bg'], match['bg'])
        self.assertEquals(expected['fs'], match['fs'])
        self.assertEquals(expected['build'], match['build'])

    def test_invalid(self):
        self.assertIsNone(_parse_assertion(''))
        self.assertIsNone(_parse_assertion('foo'))
        self.assertIsNone(_parse_assertion('// '))
        self.assertIsNone(_parse_assertion('// foo'))
        # self.assertIsNone(_parse_assertion('// ^ ^'))
        # self.assertIsNone(_parse_assertion('// ^^^ ^'))
        # self.assertIsNone(_parse_assertion('// ^ foo'))
        # self.assertIsNone(_parse_assertion('// ^ x=y'))

    def test_fg(self):
        self.assertMatch('// ^ fg=#ffffff', {'repeat': '^', 'fg': '#ffffff'})

    def test_bg(self):
        self.assertMatch('// ^ bg=#000000', {'repeat': '^', 'bg': '#000000'})

    def test_fs(self):
        self.assertMatch('// ^ fs=italic', {'repeat': '^', 'fs': 'italic'})
        self.assertMatch('// ^ fs=bold', {'repeat': '^', 'fs': 'bold'})
        self.assertMatch('// ^ fs=underline', {'repeat': '^', 'fs': 'underline'})
        self.assertMatch('// ^ fs=stippled_underline', {'repeat': '^', 'fs': 'stippled_underline'})
        self.assertMatch('// ^ fs=squiggly_underline', {'repeat': '^', 'fs': 'squiggly_underline'})
        self.assertMatch('// ^ fs=bold italic', {'repeat': '^', 'fs': 'bold italic'})
        self.assertMatch('// ^ fs=italic bold', {'repeat': '^', 'fs': 'italic bold'})
        self.assertMatch('// ^ fs=italic bold glow', {'repeat': '^', 'fs': 'italic bold glow'})
        self.assertMatch('// ^ fs=italic bold glow underline', {'repeat': '^', 'fs': 'italic bold glow underline'})
        self.assertMatch('// ^ fs=italic stippled_underline glow', {'repeat': '^', 'fs': 'italic stippled_underline glow'})  # noqa: E501
        self.assertMatch('// ^ fs=italic stippled_underline glow', {'repeat': '^', 'fs': 'italic stippled_underline glow'})  # noqa: E501
        self.assertMatch('// ^ fs=italic stippled_underline squiggly_underline', {'repeat': '^', 'fs': 'italic stippled_underline squiggly_underline'})  # noqa: E501
        self.assertMatch('// ^ fs=italic stippled_underline squiggly_underline', {'repeat': '^', 'fs': 'italic stippled_underline squiggly_underline'})  # noqa: E501
        self.assertMatch('// ^ fs=', {'repeat': '^', 'fs': ''})

    def test_build(self):
        self.assertMatch('// ^ fg=#ffffff build>=3127', {'repeat': '^', 'fg': '#ffffff', 'build': '3127'})
        self.assertMatch('// ^ bg=#000000 build>=3143', {'repeat': '^', 'bg': '#000000', 'build': '3143'})
        self.assertMatch('// ^ fs=italic build>=4000', {'repeat': '^', 'fs': 'italic', 'build': '4000'})
        self.assertMatch('// ^ fs=italic bold build>=4000', {'repeat': '^', 'fs': 'italic bold', 'build': '4000'})
        self.assertMatch('// ^ fs=italic bold stippled_underline build>=4123', {'repeat': '^', 'fs': 'italic bold stippled_underline', 'build': '4123'})  # noqa: E501
        self.assertMatch('// ^ fs= build>=4000', {'repeat': '^', 'fs': '', 'build': '4000'})

    def test_multiple_assertions(self):
        self.assertMatch('// ^ fg=#ffffff bg=#000000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000'})
        self.assertMatch('// ^ fg=#ffffff bg=#000000 build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff bg=#000000 fs=bold', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff bg=#000000 fs=bold build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff bg=#000000 fs=bold italic stippled_underline', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold italic stippled_underline'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff bg=#000000 fs=bold italic stippled_underline build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold italic stippled_underline', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff bg=#000000 fs=italic bold underline build>=3133', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'italic bold underline', 'build': '3133'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff fs=bold', {'repeat': '^', 'fg': '#ffffff', 'fs': 'bold'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff fs=', {'repeat': '^', 'fg': '#ffffff', 'fs': ''})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff fs=bold build>=4000', {'repeat': '^', 'fg': '#ffffff', 'fs': 'bold', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff fs=bold squiggly_underline glow', {'repeat': '^', 'fg': '#ffffff', 'fs': 'bold squiggly_underline glow'})  # noqa: E501
        self.assertMatch('// ^ fg=#ffffff fs=bold squiggly_underline glow build>=4000', {'repeat': '^', 'fg': '#ffffff', 'fs': 'bold squiggly_underline glow', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs=bold', {'repeat': '^', 'bg': '#000000', 'fs': 'bold'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs=bold build>=4000', {'repeat': '^', 'bg': '#000000', 'fs': 'bold', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs=bold italic', {'repeat': '^', 'bg': '#000000', 'fs': 'bold italic'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs=bold italic build>=4000', {'repeat': '^', 'bg': '#000000', 'fs': 'bold italic', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs= build>=4000', {'repeat': '^', 'bg': '#000000', 'fs': '', 'build': '4000'})  # noqa: E501

    def test_multiple_assertions_any_order(self):
        self.assertMatch('// ^ bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000'})
        self.assertMatch('// ^ bg=#000000 fg=#ffffff build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ build>=4000 bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 build>=4000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fg=#ffffff fs=bold', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fg=#ffffff fs=', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': ''})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fg=#ffffff fs=bold build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fg=#ffffff fs=bold glow squiggly_underline italic stippled_underline', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold glow squiggly_underline italic stippled_underline'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fg=#ffffff fs=bold glow squiggly_underline italic stippled_underline build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold glow squiggly_underline italic stippled_underline', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs=bold fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs=bold fg=#ffffff build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs=bold glow fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold glow'})  # noqa: E501
        self.assertMatch('// ^ bg=#000000 fs=bold glow fg=#ffffff build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold glow', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ fs=bold bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold'})  # noqa: E501
        self.assertMatch('// ^ fs= bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': ''})  # noqa: E501
        self.assertMatch('// ^ fs=bold bg=#000000 fg=#ffffff build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ build>=4000 fs=bold bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ fs=bold italic bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold italic'})  # noqa: E501
        self.assertMatch('// ^ fs=bold italic bg=#000000 fg=#ffffff build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold italic', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ fs=bold italic glow bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold italic glow'})  # noqa: E501
        self.assertMatch('// ^ fs=bold italic glow bg=#000000 fg=#ffffff build>=4000', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold italic glow', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ build>=4000 fs=bold italic glow bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': 'bold italic glow', 'build': '4000'})  # noqa: E501
        self.assertMatch('// ^ build>=4000 fs= italic glow bg=#000000 fg=#ffffff', {'repeat': '^', 'fg': '#ffffff', 'bg': '#000000', 'fs': '', 'build': '4000'})  # noqa: E501

    def test_repeats(self):
        self.assertMatch('// ^^ fg=#ffffff', {'repeat': '^^', 'fg': '#ffffff'})
        self.assertMatch('// ^^^^^^^ bg=#000000', {'repeat': '^^^^^^^', 'bg': '#000000'})
        self.assertMatch('// ^^^ fg=#ffffff bg=#000000', {'repeat': '^^^', 'fg': '#ffffff', 'bg': '#000000'})

    def test_valid_comment_markers(self):
        # start-comment, end-comment
        comments = [
            ['// ', ''],
            ['//', ''],
            ['# ', ''],
            ['/* ', ''],
            ['/* ', '*/'],
            ['-- ', ''],
            ['<!-- ', ''],
            ['<!-- ', '-->'],
        ]

        for s, e in comments:
            self.assertMatch(s + '^ fg=#ffffff' + e, {'repeat': '^', 'fg': '#ffffff'})
            self.assertMatch(s + '^ bg=#ffffff' + e, {'repeat': '^', 'bg': '#ffffff'})
            self.assertMatch(s + '^ fs=bold' + e, {'repeat': '^', 'fs': 'bold'})
            self.assertMatch(s + '^ fs=' + e, {'repeat': '^', 'fs': ''})
            self.assertMatch(s + '^ fs=bold italic' + e, {'repeat': '^', 'fs': 'bold italic'})
            self.assertMatch(s + '^ fs=bold italic stippled_underline' + e, {'repeat': '^', 'fs': 'bold italic stippled_underline'})  # noqa: E501
            self.assertMatch(s + '^ fg=#ffffff bg=#000000' + e, {'repeat': '^', 'bg': '#000000', 'fg': '#ffffff'})
            self.assertMatch(s + '^ bg=#000000 fg=#ffffff' + e, {'repeat': '^', 'bg': '#000000', 'fg': '#ffffff'})
            self.assertMatch(s + '^ fg=#ffffff fs=bold' + e, {'repeat': '^', 'fg': '#ffffff', 'fs': 'bold'})
            self.assertMatch(s + '^ fg=#ffffff fs=bold italic' + e, {'repeat': '^', 'fg': '#ffffff', 'fs': 'bold italic'})  # noqa: E501
            self.assertMatch(s + '^ fg=#ffffff fs=bold italic glow' + e, {'repeat': '^', 'fg': '#ffffff', 'fs': 'bold italic glow'})  # noqa: E501
