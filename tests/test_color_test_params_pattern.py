from unittest import TestCase

from ColorSchemeUnit.lib.runner import _color_test_params_compiled_pattern as pattern


class TestColorTestParamsPattern(TestCase):

    def test_invalid(self):
        self.assertIsNone(pattern.match(''))
        self.assertIsNone(pattern.match('foo'))
        self.assertIsNone(pattern.match('COLOR SCHEME TEST'))
        self.assertIsNone(pattern.match('COLOR SCHEME TEST ""'))
        self.assertIsNone(pattern.match('COLOR SCHEME TEST "" "y"'))
        self.assertIsNone(pattern.match('COLOR SCHEME TEST "" ""'))
        self.assertIsNone(pattern.match('FOO COLOR SCHEME TEST'))
        self.assertIsNone(pattern.match('# COLOR SCHEME TEST'))
        self.assertIsNone(pattern.match('// COLOR SCHEME TEST'))

    def test_valid(self):
        match = pattern.match('COLOR SCHEME TEST "x" "y"')
        self.assertTrue(match)
        self.assertEquals('x', match.group('color_scheme'))
        self.assertEquals('y', match.group('syntax_name'))
        self.assertEquals(match.group(0), 'COLOR SCHEME TEST "x" "y"')

    def test_allow_skipping_syntax_if_not_found(self):
        match = pattern.match('COLOR SCHEME TEST "x" SKIP IF NOT "y"')
        self.assertTrue(match)
        self.assertEquals('x', match.group('color_scheme'))
        self.assertEquals(' SKIP IF NOT', match.group('skip_if_not_syntax'))
        self.assertEquals('y', match.group('syntax_name'))
        self.assertEquals(match.group(0), 'COLOR SCHEME TEST "x" SKIP IF NOT "y"')

    def test_allows_syntax_to_be_auto_detected(self):
        match = pattern.match('COLOR SCHEME TEST "x"')
        self.assertTrue(match)
        self.assertEquals('x', match.group('color_scheme'))
        self.assertIsNone(match.group('syntax_name'))
        self.assertEquals(match.group(0), 'COLOR SCHEME TEST "x"')

    def test_valid_using_comments(self):
        comments = [  # start_comment, end_comment
            ['// ', ''],
            ['//', ''],
            ['# ', ''],
            ['/* ', ' */'],
            ['/*', '*/'],
            ['/* ', ''],
            ['-- ', ''],
            ['<!-- ', ' -->'],
            ['<!-- ', ''],
            ['<?php // ', ' ?>'],
            ['<?php // ', ''],
            ['<?php /* ', ''],
        ]

        for start_comment, end_comment in comments:
            match = pattern.match(start_comment + 'COLOR SCHEME TEST "x" "y"' + end_comment)
            self.assertTrue(match)
            self.assertEquals('x', match.group('color_scheme'))
            self.assertEquals('y', match.group('syntax_name'))
            self.assertEquals(match.group(0), start_comment + 'COLOR SCHEME TEST "x" "y"' + end_comment)

    def test_doesnt_include_trailing_whitespace(self):
        match = pattern.match('COLOR SCHEME TEST "x" "y"        ')
        self.assertTrue(match)
        self.assertEquals(match.group(0), 'COLOR SCHEME TEST "x" "y"')
