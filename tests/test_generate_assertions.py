from textwrap import dedent
from unittest import TestCase

from ColorSchemeUnit.lib.generator import _build_assertions


class TestGenerateAssertions(TestCase):

    def test_generate_assertions(self):
        self.assertEquals(dedent("""
        ^ a
        """).strip(), _build_assertions(['a'], '', ''))

        self.assertEquals(dedent("""
        ^ a
         ^ b
        """).strip(), _build_assertions(['a', 'b'], '', ''))

        self.assertEquals(dedent("""
        ^ a
         ^ b
          ^ c
        """).strip(), _build_assertions(['a', 'b', 'c'], '', ''))

    def test_generate_repeat_assertions(self):
        self.assertEquals(dedent("""
        ^^^ a
        """).strip(), _build_assertions(['a', 'a', 'a'], '', ''))

        self.assertEquals(dedent("""
        ^^^ a
           ^^ b
        """).strip(), _build_assertions(['a', 'a', 'a', 'b', 'b'], '', ''))

        self.assertEquals(dedent("""
        ^^^ a
           ^^ b
             ^ c
              ^^^ d
        """).strip(), _build_assertions(['a', 'a', 'a', 'b', 'b', 'c', 'd', 'd', 'd'], '', ''))

    def test_generate_assertions_with_comment_start(self):
        self.assertEquals('', _build_assertions(['a'], '#', ''))

        self.assertEquals(dedent("""
        #^ b
        """).strip(), _build_assertions(['a', 'b'], '#', ''))

        self.assertEquals(dedent("""
        #^ b
        # ^ c
        """).strip(), _build_assertions(['a', 'b', 'c'], '#', ''))

        self.assertEquals(dedent("""
        #^ b
        # ^ c
        #  ^ d
        """).strip(), _build_assertions(['a', 'b', 'c', 'd'], '#', ''))

    def test_generate_assertions_with_blanks(self):
        self.assertEquals(dedent("""
        ^ a
          ^ b
        """).strip(), _build_assertions(['a', '', 'b'], '', ''))

        self.assertEquals(dedent("""
        ^ a
           ^ b
        """).strip(), _build_assertions(['a', '', '', 'b'], '', ''))

        self.assertEquals(dedent("""
        ^ a
           ^ b
            ^ c
                ^ d
        """).strip(), _build_assertions(['a', '', '', 'b', 'c', '', '', '', 'd'], '', ''))

        self.assertEquals(dedent("""
        #^ a
        #  ^ b
        """).strip(), _build_assertions(['a', 'a', '', 'b'], '#', ''))

    def test_generate_assertions_that_ends_in_blanks(self):
        self.assertEquals(dedent("""
        ^ a
        """).strip(), _build_assertions(['a', ''], '', ''))

        self.assertEquals(dedent("""
        ^ a
        """).strip(), _build_assertions(['a', '', '', ''], '', ''))

        self.assertEquals(dedent("""
        #^ a
        """).strip(), _build_assertions(['a', 'a', '', '', ''], '#', ''))
