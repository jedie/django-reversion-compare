
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

def html_diff(value1, value2, cleanup=SEMANTIC):
    """
    Generates a diff used google-diff-match-patch is exist or ndiff as fallback
    
    The cleanup parameter can be SEMANTIC, EFFICIENCY or None to clean up the diff
    for greater human readibility.
    """
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
