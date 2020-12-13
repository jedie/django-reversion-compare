from reversion_compare.helpers import EFFICIENCY, SEMANTIC, generate_dmp_diff, generate_ndiff, html_diff, diff2lines, lines2html


def test_generate_ndiff():
    html = generate_ndiff(
        value1='one',
        value2='two',
    )
    assert html == (
        '<pre class="highlight">'
        '<del>- one</del>\n'
        '<ins>+ two</ins>'
        '</pre>'
    )

    html = generate_ndiff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
    )
    assert html == (
        '<pre class="highlight">'
        '  aaa\n'
        '<ins>+ bbb</ins>\n'
        '  ccc\n'
        '<del>- ddd</del>'
        '</pre>'
    )


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
    html = generate_dmp_diff(
        value1='one',
        value2='two',
        cleanup=None
    )
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins"><ins>tw</ins>o<del>ne</del></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=None
    )
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
    html = generate_dmp_diff(
        value1='one',
        value2='two',
        cleanup=EFFICIENCY
    )
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins"><ins>tw</ins>o<del>ne</del></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=EFFICIENCY
    )
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
    html = generate_dmp_diff(
        value1='xxx1xxx\nX',
        value2='xxx2xxx\nX',
        cleanup=SEMANTIC
    )
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins">xxx<del>1</del><ins>2</ins>xxx</span>\n'
        'X\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='one',
        value2='two',
        cleanup=SEMANTIC
    )
    assert html == (
        '<pre class="highlight">'
        '<span class="diff-line diff-del diff-ins"><del>one</del><ins>two</ins></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=SEMANTIC
    )
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
        '<span class="diff-line diff-del diff-ins"><del>m</del><ins>M</ins>ore than 20 <del>C</del><ins>c</ins>haracters<ins>,</ins> or?</span>\n'
        '</pre>'
    )

def test_diff2lines():
    assert diff2lines(
        [
            (0, "equal\ntext"),
            (-1, "deleted\n"),
            (1, "added\ntext"),
        ]
    ) == [
        [(0, "equal")],
        [(0, "text"), (-1, "deleted")],
        [(1, "added")],
        [(1, "text")],
    ]

    # html escaping
    assert diff2lines(
        [
            (0, "<equal>\ntext"),
            (-1, "&deleted\n"),
            (1, "added\ntext"),
        ]
    ) == [
        [(0, "&lt;equal&gt;")],
        [(0, "text"), (-1, "&amp;deleted")],
        [(1, "added")],
        [(1, "text")],
    ]

    # \r\n line feeds
    assert diff2lines(
        [
            (0, "equal\r\ntext"),
            (-1, "deleted\r\n"),
            (1, "added\r\ntext"),
        ]
    ) == [
        [(0, "equal")],
        [(0, "text"), (-1, "deleted")],
        [(1, "added")],
        [(1, "text")],
    ]

    # Whitespace is retained
    assert diff2lines(
        [
            (0, "equal\ntext   "),
            (-1, "deleted\n"),
            (1, "added\n   text"),
        ]
    ) == [
        [(0, "equal")],
        [(0, "text   "), (-1, "deleted")],
        [(1, "added")],
        [(1, "   text")],
    ]

def test_lines2html():
    assert lines2html(
        [
            [(0, "equal")],
            [(0, "text"), (-1, "deleted"), (-1, '')],
            [(1, "added")],
            [(1, "text"), (-1, "removed")],
        ]
    ) == (
        "equal\n"
        '<span class="diff-line diff-del">text<del>deleted</del><del>⏎</del></span>\n'
        '<span class="diff-line diff-ins"><ins>added</ins></span>\n'
        '<span class="diff-line diff-del diff-ins"><ins>text</ins><del>removed</del></span>\n'
    )
