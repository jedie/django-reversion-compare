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


def test_generate_ndiff():
    html = generate_ndiff(
        value1='one',
        value2='two',
    )
    assert html == ('<pre class="highlight">' '<del>- one</del>\n' '<ins>+ two</ins>' '</pre>')

    html = generate_ndiff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
    )
    assert html == ('<pre class="highlight">' '  aaa\n' '<ins>+ bbb</ins>\n' '  ccc\n' '<del>- ddd</del>' '</pre>')


def test_generate_dmp_diff():
    html = generate_dmp_diff(
        value1='one',
        value2='two',
    )
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins"><del>one</del><ins>two</ins></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
    )
    assert html == (
        '<pre class="highlight">aaa\n'
        '<span class="diff-line diff-del"><del>ccc</del></span>\n'
        '<span class="diff-line diff-del diff-ins"><del>ddd</del><ins>bbb</ins></span>\n'
        '<span class="diff-line diff-ins"><ins>ccc</ins></span>\n'
        '</pre>'
    )


def test_generate_dmp_diff_no_cleanup():
    """
    Test diffs created by google "diff-match-patch" without cleanup
    """
    html = generate_dmp_diff(value1='one', value2='two', cleanup=None)
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins"><ins>tw</ins>o<del>ne</del></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(value1='aaa\nccc\nddd\n', value2='aaa\nbbb\nccc\n', cleanup=None)
    assert html == (
        '<pre class="highlight">aaa\n'
        '<span class="diff-line diff-ins"><ins>bbb</ins></span>\n'
        'ccc\n'
        '<span class="diff-line diff-del"><del>ddd</del></span>\n'
        '</pre>'
    )


def test_generate_dmp_diff_efficiency():
    """
    Test diffs created by google "diff-match-patch" with "efficiency" cleanup
    """
    html = generate_dmp_diff(value1='one', value2='two', cleanup=EFFICIENCY)
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins"><ins>tw</ins>o<del>ne</del></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(value1='aaa\nccc\nddd\n', value2='aaa\nbbb\nccc\n', cleanup=EFFICIENCY)
    assert html == (
        '<pre class="highlight">aaa\n'
        '<span class="diff-line diff-ins"><ins>bbb</ins></span>\n'
        'ccc\n'
        '<span class="diff-line diff-del"><del>ddd</del></span>\n'
        '</pre>'
    )


def test_generate_dmp_diff_semantic():
    """
    Test diffs created by google "diff-match-patch" with "semantic" cleanup
    """
    html = generate_dmp_diff(value1='xxx1xxx\nX', value2='xxx2xxx\nX', cleanup=SEMANTIC)
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins">xxx<del>1</del><ins>2</ins>xxx</span>\n'
        'X\n'
        '</pre>'
    )

    html = generate_dmp_diff(value1='one', value2='two', cleanup=SEMANTIC)
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins"><del>one</del><ins>two</ins></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(value1='aaa\nccc\nddd\n', value2='aaa\nbbb\nccc\n', cleanup=SEMANTIC)
    assert html == (
        '<pre class="highlight">aaa\n'
        '<span class="diff-line diff-del"><del>ccc</del></span>\n'
        '<span class="diff-line diff-del diff-ins"><del>ddd</del><ins>bbb</ins></span>\n'
        '<span class="diff-line diff-ins"><ins>ccc</ins></span>\n'
        '</pre>'
    )


def test_html_diff():
    # small values -> ndiff
    html = html_diff(
        value1='one',
        value2='two',
    )
    assert html == '<pre class="highlight"><del>- one</del>\n<ins>+ two</ins></pre>'

    # big values -> Google diff-match-patch
    html = html_diff(
        value1='more than 20 Characters or?',
        value2='More than 20 characters, or?',
    )
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins">'
        '<del>m</del><ins>M</ins>ore than 20 <del>C</del><ins>c</ins>haracters<ins>,</ins> or?'
        '</span>\n'
        '</pre>'
    )


def test_diff2lines():
    assert list(
        diff2lines(
            [
                (DIFF_EQUAL, 'equal\ntext'),
                (DIFF_DELETE, 'deleted\n'),
                (DIFF_INSERT, 'added\ntext'),
            ]
        )
    ) == [
        [(DIFF_EQUAL, 'equal')],
        [(DIFF_EQUAL, 'text'), (DIFF_DELETE, 'deleted')],
        [(DIFF_INSERT, 'added')],
        [(DIFF_INSERT, 'text')],
    ]

    # html escaping
    assert list(
        diff2lines(
            [
                (DIFF_EQUAL, '<equal>\ntext'),
                (DIFF_DELETE, '&deleted\n'),
                (DIFF_INSERT, 'added\ntext'),
            ]
        )
    ) == [
        [(DIFF_EQUAL, '&lt;equal&gt;')],
        [(DIFF_EQUAL, 'text'), (DIFF_DELETE, '&amp;deleted')],
        [(DIFF_INSERT, 'added')],
        [(DIFF_INSERT, 'text')],
    ]

    # \r\n line feeds
    assert list(
        diff2lines(
            [
                (DIFF_EQUAL, 'equal\r\ntext'),
                (DIFF_DELETE, 'deleted\r\n'),
                (DIFF_INSERT, 'added\r\ntext'),
            ]
        )
    ) == [
        [(DIFF_EQUAL, 'equal')],
        [(DIFF_EQUAL, 'text'), (DIFF_DELETE, 'deleted')],
        [(DIFF_INSERT, 'added')],
        [(DIFF_INSERT, 'text')],
    ]

    # Whitespace is retained
    assert list(
        diff2lines(
            [
                (DIFF_EQUAL, 'equal\ntext   '),
                (DIFF_DELETE, 'deleted\n'),
                (DIFF_INSERT, 'added\n   text'),
            ]
        )
    ) == [
        [(DIFF_EQUAL, 'equal')],
        [(DIFF_EQUAL, 'text   '), (DIFF_DELETE, 'deleted')],
        [(DIFF_INSERT, 'added')],
        [(DIFF_INSERT, '   text')],
    ]


def test_lines2html():
    assert lines2html(
        [
            [(DIFF_EQUAL, 'equal')],
            [(DIFF_EQUAL, 'text'), (DIFF_DELETE, 'deleted'), (DIFF_DELETE, '')],
            [(DIFF_INSERT, 'added')],
            [(DIFF_INSERT, 'text'), (DIFF_DELETE, 'removed')],
        ]
    ) == (
        'equal\n'
        '<span class="diff-line diff-del">text<del>deleted</del><del>⏎</del></span>\n'
        '<span class="diff-line diff-ins"><ins>added</ins></span>\n'
        '<span class="diff-line diff-del diff-ins"><ins>text</ins><del>removed</del></span>\n'
    )
