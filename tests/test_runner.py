import os

import sublime

from ColorSchemeUnit.tests import unittest

from ColorSchemeUnit.lib.coverage import Coverage
from ColorSchemeUnit.lib.result import ResultPrinter
from ColorSchemeUnit.lib.test import TestOutputPanel
from ColorSchemeUnit.lib.runner import run_color_scheme_test


class TestOutputMock(TestOutputPanel):

    def show(self):
        pass


class TestRunner(unittest.ViewTestCase):

    def setUp(self):
        super().setUp()
        self.output = TestOutputMock(self.view.window())
        self.result_printer = ResultPrinter(self.output)
        self.code_coverage = Coverage(
            self.output,
            enabled=False,
            is_single_file=False)

    def runTest(self, test: str) -> dict:
        result = run_color_scheme_test(
            test,
            self.view.window(),
            self.result_printer,
            self.code_coverage)

        return result

    def assertOutput(self, expected: str) -> None:
        self.assertEquals(expected, self.output.view.substr(sublime.Region(0, self.output.view.size())))

    def resolveTestFile(self, test) -> str:
        return os.path.join(os.path.dirname(sublime.packages_path()), test)

    def test_run_color_scheme_test(self):
        test = 'Packages/ColorSchemeUnit/tests/fixtures/test.php'
        result = self.runTest(test)

        self.assertEquals({
            'skip': {},
            'error': {},
            'failures': [
                {
                    'actual': {
                        'fontStyle': 'italic',
                        'foreground': '#66d9ef'
                    },
                    'assertion': '//  ^ fg=#66d9ef fs=',
                    'col': 5,
                    'expected': {
                        'fontStyle': '',
                        'foreground': '#66d9ef'
                    },
                    'file': self.resolveTestFile(test),
                    'row': 3
                }
            ],
            'assertions': 1
        }, result)
        self.assertOutput('F')
