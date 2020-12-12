from reversion_compare.helpers import EFFICIENCY, SEMANTIC, generate_dmp_diff, generate_ndiff, html_diff


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
        '<span class="diff-line"><del>one</del></span>\n'
        '<span class="diff-line"><ins>two</ins></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
    )
    assert html == (
        '<pre class="highlight">aaa\n\n'
        '<span class="diff-line"><del>ccc</span>\n'
        'ddd</del>\n'
        '<span class="diff-line">'
        '<ins>bbb</span>\n'
        'ccc</ins>\n\n\n'
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
        '<span class="diff-line"><ins>tw</ins></span>\n'
        'o\n'
        '<span class="diff-line"><del>ne</del></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=None
    )
    assert html == (
        '<pre class="highlight">aaa\n\n'
        '<span class="diff-line"><ins>bbb</span>\n'
        '</ins>\nccc\n\n'
        '<span class="diff-line"><del>ddd</span>\n'
        '</del>\n'
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
        '<span class="diff-line"><ins>tw</ins></span>\n'
        'o\n'
        '<span class="diff-line"><del>ne</del></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=EFFICIENCY
    )
    assert html == (
        '<pre class="highlight">aaa\n\n'
        '<span class="diff-line"><ins>bbb</span>\n'
        '</ins>\nccc\n\n'
        '<span class="diff-line"><del>ddd</span>\n'
        '</del>\n'
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
        '<pre class="highlight">xxx\n'
        '<span class="diff-line"><del>1</del></span>\n'
        '<span class="diff-line"><ins>2</ins></span>\n'
        'xxx\n'
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
        '<span class="diff-line"><del>one</del></span>\n'
        '<span class="diff-line"><ins>two</ins></span>\n'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=SEMANTIC
    )
    assert html == (
        '<pre class="highlight">aaa\n\n'
        '<span class="diff-line"><del>ccc</span>\n'
        'ddd</del>\n'
        '<span class="diff-line"><ins>bbb</span>\n'
        'ccc</ins>\n\n\n'
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
        '<span class="diff-line"><del>m</del></span>\n'
        '<span class="diff-line"><ins>M</ins></span>\n'
        'ore than 20 \n'
        '<span class="diff-line"><del>C</del></span>\n'
        '<span class="diff-line"><ins>c</ins></span>\n'
        'haracters\n<span class="diff-line"><ins>,</ins></span>\n'
        ' or?\n'
        '</pre>'
    )
