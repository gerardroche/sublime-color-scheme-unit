from textwrap import dedent
from unittest import TestCase

from color_scheme_unit.plugin import _generate_assertions


class TestGenerateAssertions(TestCase):

    def test_generate_assertions(self):
        self.assertEquals(dedent("""
        ^ a
        """).lstrip(), _generate_assertions(['a'], '', ''))

        self.assertEquals(dedent("""
        ^ a
         ^ b
        """).lstrip(), _generate_assertions(['a', 'b'], '', ''))

        self.assertEquals(dedent("""
        ^ a
         ^ b
          ^ c
        """).lstrip(), _generate_assertions(['a', 'b', 'c'], '', ''))

    def test_generate_repeat_assertions(self):
        self.assertEquals(dedent("""
        ^^^ a
        """).lstrip(), _generate_assertions(['a', 'a', 'a'], '', ''))

        self.assertEquals(dedent("""
        ^^^ a
           ^^ b
        """).lstrip(), _generate_assertions(['a', 'a', 'a', 'b', 'b'], '', ''))

        self.assertEquals(dedent("""
        ^^^ a
           ^^ b
             ^ c
              ^^^ d
        """).lstrip(), _generate_assertions(['a', 'a', 'a', 'b', 'b', 'c', 'd', 'd', 'd'], '', ''))

    def test_generate_assertions_with_comment_start(self):
        self.assertEquals('', _generate_assertions(['a'], '#', ''))

        self.assertEquals(dedent("""
        #^ b
        """).lstrip(), _generate_assertions(['a', 'b'], '#', ''))

        self.assertEquals(dedent("""
        #^ b
        # ^ c
        """).lstrip(), _generate_assertions(['a', 'b', 'c'], '#', ''))

        self.assertEquals(dedent("""
        #^ b
        # ^ c
        #  ^ d
        """).lstrip(), _generate_assertions(['a', 'b', 'c', 'd'], '#', ''))
