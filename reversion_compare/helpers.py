"""
    django-reversion helpers
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    A number of useful helper functions to automate common tasks.
    
    Used google-diff-match-patch [1] if installed, fallback to difflib.
    For installing use e.g. the unofficial package:
    
        pip install diff-match-patch
    
    [1] http://code.google.com/p/google-diff-match-patch/
"""


import difflib

from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

try:
    # http://code.google.com/p/google-diff-match-patch/
    from diff_match_patch import diff_match_patch
except ImportError:
    google_diff_match_patch = False
else:
    google_diff_match_patch = True
    dmp = diff_match_patch()
#google_diff_match_patch = False # manually disable, for testing


def highlight_diff(diff_text):
    """
    Simple highlight a diff text in the way pygments do it ;)
    """
    html = ['<pre class="highlight">']
    for line in diff_text.splitlines():
        line = escape(line)
        if line.startswith("+"):
            line = '<ins>%s</ins>' % line
        elif line.startswith("-"):
            line = '<del>%s</del>' % line

        html.append(line)
    html.append("</pre>")
    html = "\n".join(html)

    return html


SEMANTIC = 1
EFFICIENCY = 2

# Change from ndiff to unified_diff if old/new values are more than X lines:
LINE_COUNT_4_UNIFIED_DIFF = 4

def unified_diff(a, b, n=3, lineterm='\n'):
    r"""
    simmilar to the original difflib.unified_diff except:
        - no fromfile/tofile and no fromfiledate/tofiledate info lines
        - newline before diff control lines and not after

    Example:

    >>> for line in unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), lineterm=''):
    ...     print line                  # doctest: +NORMALIZE_WHITESPACE
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four
    """
    started = False
    for group in difflib.SequenceMatcher(None, a, b).get_grouped_opcodes(n):
        first, last = group[0], group[-1]
        try:
            file1_range = difflib._format_range_unified(first[1], last[2])
            file2_range = difflib._format_range_unified(first[3], last[4])
        except AttributeError:
            # difflib._format_range_unified() is new in python 2.7
            # see also: https://github.com/jedie/django-reversion-compare/issues/5
            i1, i2, j1, j2 = first[1], last[2], first[3], last[4]
            file1_range = "%i,%i" % (i1 + 1, i2 - i1)
            file2_range = "%i,%i" % (j1 + 1, j2 - j1)

        if not started:
            started = True
            yield '@@ -{} +{} @@'.format(file1_range, file2_range)
        else:
            yield '{}@@ -{} +{} @@'.format(lineterm, file1_range, file2_range)

        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in a[i1:i2]:
                    yield ' ' + line
                continue
            if tag in ('replace', 'delete'):
                for line in a[i1:i2]:
                    yield '-' + line
            if tag in ('replace', 'insert'):
                for line in b[j1:j2]:
                    yield '+' + line


def html_diff(value1, value2, cleanup=SEMANTIC):
    """
    Generates a diff used google-diff-match-patch is exist or ndiff as fallback
    
    The cleanup parameter can be SEMANTIC, EFFICIENCY or None to clean up the diff
    for greater human readibility.
    """
    value1 = force_unicode(value1)
    value2 = force_unicode(value2)
    if google_diff_match_patch:
        # Generate the diff with google-diff-match-patch
        diff = dmp.diff_main(value1, value2)
        if cleanup == SEMANTIC:
            dmp.diff_cleanupSemantic(diff)
        elif cleanup == EFFICIENCY:
            dmp.diff_cleanupEfficiency(diff)
        elif cleanup is not None:
            raise ValueError("cleanup parameter should be one of SEMANTIC, EFFICIENCY or None.")
        html = dmp.diff_prettyHtml(diff)
        html = html.replace("&para;<br>", "</br>") # IMHO mark paragraphs are needlessly
    else:
        # fallback: use built-in difflib
        value1 = value1.splitlines()
        value2 = value2.splitlines()

        if len(value1) > LINE_COUNT_4_UNIFIED_DIFF or len(value2) > LINE_COUNT_4_UNIFIED_DIFF:
            diff = unified_diff(value1, value2, n=2)
        else:
            diff = difflib.ndiff(value1, value2)

        diff_text = "\n".join(diff)
        html = highlight_diff(diff_text)

    html = mark_safe(html)

    return html


def compare_queryset(first, second):
    """
    Simple compare two querysets (used for many-to-many field compare)
    XXX: resort results?
    """
    result = []
    for item in set(first).union(set(second)):
        if item not in first: # item was inserted
            item.insert = True
        elif item not in second: # item was deleted
            item.delete = True
        result.append(item)
    return result


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
