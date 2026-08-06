import unittest

from diff_match_patch import diff_match_patch

from reversion_compare.helpers import (
    EFFICIENCY,
    SEMANTIC,
    diff2lines,
    generate_dmp_diff,
    generate_ndiff,
    html_diff,
    lines2html,
)


DIFF_EQUAL = diff_match_patch.DIFF_EQUAL
DIFF_INSERT = diff_match_patch.DIFF_INSERT
DIFF_DELETE = diff_match_patch.DIFF_DELETE


class GenerateNdiffTestCase(unittest.TestCase):
    def test_simple(self):
        html = generate_ndiff(value1='one', value2='two')
        self.assertEqual(html, '<pre class="highlight"><del>- one</del>\n<ins>+ two</ins></pre>')

    def test_multiline(self):
        html = generate_ndiff(value1='aaa\nccc\nddd\n', value2='aaa\nbbb\nccc\n')
        self.assertEqual(
            html,
            '<pre class="highlight">  aaa\n<ins>+ bbb</ins>\n  ccc\n<del>- ddd</del></pre>',
        )


class GenerateDmpDiffTestCase(unittest.TestCase):
    def test_simple(self):
        html = generate_dmp_diff(value1='one', value2='two')
        self.assertEqual(
            html,
            '<pre class="highlight">'
            '<span class="diff-line diff-del diff-ins"><del>one</del><ins>two</ins></span>\n'
            '</pre>',
        )

    def test_multiline(self):
        html = generate_dmp_diff(value1='aaa\nccc\nddd\n', value2='aaa\nbbb\nccc\n')
        self.assertEqual(
            html,
            '<pre class="highlight">aaa\n'
            '<span class="diff-line diff-del"><del>ccc</del></span>\n'
            '<span class="diff-line diff-del diff-ins"><del>ddd</del><ins>bbb</ins></span>\n'
            '<span class="diff-line diff-ins"><ins>ccc</ins></span>\n'
            '</pre>',
        )

    def test_no_cleanup_simple(self):
        """
        Test diffs created by google "diff-match-patch" without cleanup
        """
        html = generate_dmp_diff(value1='one', value2='two', cleanup=None)
        self.assertEqual(
            html,
            '<pre class="highlight">'
            '<span class="diff-line diff-del diff-ins"><ins>tw</ins>o<del>ne</del></span>\n'
            '</pre>',
        )

    def test_no_cleanup_multiline(self):
        """
        Test diffs created by google "diff-match-patch" without cleanup
        """
        html = generate_dmp_diff(value1='aaa\nccc\nddd\n', value2='aaa\nbbb\nccc\n', cleanup=None)
        self.assertEqual(
            html,
            '<pre class="highlight">aaa\n'
            '<span class="diff-line diff-ins"><ins>bbb</ins></span>\n'
            'ccc\n'
            '<span class="diff-line diff-del"><del>ddd</del></span>\n'
            '</pre>',
        )

    def test_efficiency_simple(self):
        """
        Test diffs created by google "diff-match-patch" with "efficiency" cleanup
        """
        html = generate_dmp_diff(value1='one', value2='two', cleanup=EFFICIENCY)
        self.assertEqual(
            html,
            '<pre class="highlight">'
            '<span class="diff-line diff-del diff-ins"><ins>tw</ins>o<del>ne</del></span>\n'
            '</pre>',
        )

    def test_efficiency_multiline(self):
        """
        Test diffs created by google "diff-match-patch" with "efficiency" cleanup
        """
        html = generate_dmp_diff(value1='aaa\nccc\nddd\n', value2='aaa\nbbb\nccc\n', cleanup=EFFICIENCY)
        self.assertEqual(
            html,
            '<pre class="highlight">aaa\n'
            '<span class="diff-line diff-ins"><ins>bbb</ins></span>\n'
            'ccc\n'
            '<span class="diff-line diff-del"><del>ddd</del></span>\n'
            '</pre>',
        )

    def test_semantic_word(self):
        """
        Test diffs created by google "diff-match-patch" with "semantic" cleanup
        """
        html = generate_dmp_diff(value1='xxx1xxx\nX', value2='xxx2xxx\nX', cleanup=SEMANTIC)
        self.assertEqual(
            html,
            '<pre class="highlight">'
            '<span class="diff-line diff-del diff-ins">xxx<del>1</del><ins>2</ins>xxx</span>\n'
            'X\n'
            '</pre>',
        )

    def test_semantic_simple(self):
        """
        Test diffs created by google "diff-match-patch" with "semantic" cleanup
        """
        html = generate_dmp_diff(value1='one', value2='two', cleanup=SEMANTIC)
        self.assertEqual(
            html,
            '<pre class="highlight">'
            '<span class="diff-line diff-del diff-ins"><del>one</del><ins>two</ins></span>\n'
            '</pre>',
        )

    def test_semantic_multiline(self):
        """
        Test diffs created by google "diff-match-patch" with "semantic" cleanup
        """
        html = generate_dmp_diff(value1='aaa\nccc\nddd\n', value2='aaa\nbbb\nccc\n', cleanup=SEMANTIC)
        self.assertEqual(
            html,
            '<pre class="highlight">aaa\n'
            '<span class="diff-line diff-del"><del>ccc</del></span>\n'
            '<span class="diff-line diff-del diff-ins"><del>ddd</del><ins>bbb</ins></span>\n'
            '<span class="diff-line diff-ins"><ins>ccc</ins></span>\n'
            '</pre>',
        )


class HtmlDiffTestCase(unittest.TestCase):
    def test_small_values_use_ndiff(self):
        # small values -> ndiff
        html = html_diff(value1='one', value2='two')
        self.assertEqual(html, '<pre class="highlight"><del>- one</del>\n<ins>+ two</ins></pre>')

    def test_big_values_use_dmp(self):
        # big values -> Google diff-match-patch
        html = html_diff(
            value1='more than 20 Characters or?',
            value2='More than 20 characters, or?',
        )
        self.assertEqual(
            html,
            '<pre class="highlight">'
            '<span class="diff-line diff-del diff-ins">'
            '<del>m</del><ins>M</ins>ore than 20 <del>C</del><ins>c</ins>haracters<ins>,</ins> or?'
            '</span>\n'
            '</pre>',
        )


class Diff2LinesTestCase(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            list(
                diff2lines(
                    [
                        (DIFF_EQUAL, 'equal\ntext'),
                        (DIFF_DELETE, 'deleted\n'),
                        (DIFF_INSERT, 'added\ntext'),
                    ]
                )
            ),
            [
                [(DIFF_EQUAL, 'equal')],
                [(DIFF_EQUAL, 'text'), (DIFF_DELETE, 'deleted')],
                [(DIFF_INSERT, 'added')],
                [(DIFF_INSERT, 'text')],
            ],
        )

    def test_html_escaping(self):
        self.assertEqual(
            list(
                diff2lines(
                    [
                        (DIFF_EQUAL, '<equal>\ntext'),
                        (DIFF_DELETE, '&deleted\n'),
                        (DIFF_INSERT, 'added\ntext'),
                    ]
                )
            ),
            [
                [(DIFF_EQUAL, '&lt;equal&gt;')],
                [(DIFF_EQUAL, 'text'), (DIFF_DELETE, '&amp;deleted')],
                [(DIFF_INSERT, 'added')],
                [(DIFF_INSERT, 'text')],
            ],
        )

    def test_crlf_line_feeds(self):
        self.assertEqual(
            list(
                diff2lines(
                    [
                        (DIFF_EQUAL, 'equal\r\ntext'),
                        (DIFF_DELETE, 'deleted\r\n'),
                        (DIFF_INSERT, 'added\r\ntext'),
                    ]
                )
            ),
            [
                [(DIFF_EQUAL, 'equal')],
                [(DIFF_EQUAL, 'text'), (DIFF_DELETE, 'deleted')],
                [(DIFF_INSERT, 'added')],
                [(DIFF_INSERT, 'text')],
            ],
        )

    def test_whitespace_retained(self):
        self.assertEqual(
            list(
                diff2lines(
                    [
                        (DIFF_EQUAL, 'equal\ntext   '),
                        (DIFF_DELETE, 'deleted\n'),
                        (DIFF_INSERT, 'added\n   text'),
                    ]
                )
            ),
            [
                [(DIFF_EQUAL, 'equal')],
                [(DIFF_EQUAL, 'text   '), (DIFF_DELETE, 'deleted')],
                [(DIFF_INSERT, 'added')],
                [(DIFF_INSERT, '   text')],
            ],
        )


class Lines2HtmlTestCase(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            lines2html(
                [
                    [(DIFF_EQUAL, 'equal')],
                    [(DIFF_EQUAL, 'text'), (DIFF_DELETE, 'deleted'), (DIFF_DELETE, '')],
                    [(DIFF_INSERT, 'added')],
                    [(DIFF_INSERT, 'text'), (DIFF_DELETE, 'removed')],
                ]
            ),
            'equal\n'
            '<span class="diff-line diff-del">text<del>deleted</del><del>⏎</del></span>\n'
            '<span class="diff-line diff-ins"><ins>added</ins></span>\n'
            '<span class="diff-line diff-del diff-ins"><ins>text</ins><del>removed</del></span>\n',
        )
