from reversion_compare.helpers import EFFICIENCY, SEMANTIC, dmp, generate_dmp_diff, generate_ndiff, html_diff


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
    assert html == '<pre class="highlight"><del>one</del><ins>two</ins></pre>'

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
    )
    assert html == (
        '<pre class="highlight">aaa\n'
        '<del>ccc\n'
        'ddd</del><ins>bbb\n'
        'ccc</ins>\n'
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
    assert html == '<pre class="highlight"><ins>tw</ins>o<del>ne</del></pre>'

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=None
    )
    assert html == (
        '<pre class="highlight">'
        'aaa\n'
        '<ins>bbb\n'
        '</ins>ccc\n'
        '<del>ddd\n'
        '</del>'
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
    assert html == '<pre class="highlight"><ins>tw</ins>o<del>ne</del></pre>'

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=EFFICIENCY
    )
    assert html == (
        '<pre class="highlight">'
        'aaa\n'
        '<ins>bbb\n'
        '</ins>ccc\n'
        '<del>ddd\n'
        '</del>'
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
        'xxx<del>1</del><ins>2</ins>xxx\n'
        'X'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='one',
        value2='two',
        cleanup=SEMANTIC
    )
    assert html == (
        '<pre class="highlight">'
        '<del>one</del><ins>two</ins>'
        '</pre>'
    )

    html = generate_dmp_diff(
        value1='aaa\nccc\nddd\n',
        value2='aaa\nbbb\nccc\n',
        cleanup=SEMANTIC
    )
    assert html == (
        '<pre class="highlight">'
        'aaa\n'
        '<del>ccc\n'
        'ddd</del><ins>bbb\n'
        'ccc</ins>\n'
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
        '<del>m</del><ins>M</ins>ore than 20 <del>C</del><ins>c</ins>haracters<ins>,</ins> or?'
        '</pre>'
    )
