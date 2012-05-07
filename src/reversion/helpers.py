"""A number of useful helper functions to automate common tasks."""


import difflib

from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.utils.html import escape
from django.utils.safestring import mark_safe



def patch_admin(model, admin_site=None):
    """
    Enables version control with full admin integration for a model that has
    already been registered with the django admin site.
    
    This is excellent for adding version control to existing Django contrib
    applications. 
    """
    from reversion.admin import VersionAdmin # against import-loops

    admin_site = admin_site or admin.site
    try:
        ModelAdmin = admin_site._registry[model].__class__
    except KeyError:
        raise NotRegistered, "The model %r has not been registered with the admin site." % model
    # Unregister existing admin class.
    admin_site.unregister(model)
    # Register patched admin class.
    class PatchedModelAdmin(VersionAdmin, ModelAdmin):
        pass
    admin_site.register(model, PatchedModelAdmin)


# Patch generation methods, only available if the google-diff-match-patch
# library is installed.
#
# http://code.google.com/p/google-diff-match-patch/


try:
    from diff_match_patch import diff_match_patch
except ImportError:
    pass
else:
    dmp = diff_match_patch()

    def generate_diffs(old_version, new_version, field_name, cleanup):
        """Generates a diff array for the named field between the two versions."""
        # Extract the text from the versions.
        old_text = old_version.field_dict[field_name] or u""
        new_text = new_version.field_dict[field_name] or u""
        # Generate the patch.
        diffs = dmp.diff_main(unicode(old_text), unicode(new_text))
        if cleanup == "semantic":
            dmp.diff_cleanupSemantic(diffs)
        elif cleanup == "efficiency":
            dmp.diff_cleanupEfficiency(diffs)
        elif cleanup is None:
            pass
        else:
            raise ValueError("cleanup parameter should be one of 'semantic', 'efficiency' or None.")
        return diffs

    def generate_patch(old_version, new_version, field_name, cleanup=None):
        """
        Generates a text patch of the named field between the two versions.
        
        The cleanup parameter can be None, "semantic" or "efficiency" to clean up the diff
        for greater human readibility.
        """
        diffs = generate_diffs(old_version, new_version, field_name, cleanup)
        patch = dmp.patch_make(diffs)
        return dmp.patch_toText(patch)

    def generate_patch_html(old_version, new_version, field_name, cleanup=None):
        """
        Generates a pretty html version of the differences between the named 
        field in two versions.
        
        The cleanup parameter can be None, "semantic" or "efficiency" to clean up the diff
        for greater human readibility.
        """
        diffs = generate_diffs(old_version, new_version, field_name, cleanup)
        return dmp.diff_prettyHtml(diffs)


def highlight_diff(diff_text):
    """
    FIXME: How to add the style better?
    """
    try:
        from pygments import highlight
        from pygments.lexers import DiffLexer
        from pygments.formatters import HtmlFormatter
    except ImportError:
        html = "<pre>%s</pre>" % escape(diff_text)
    else:
        formatter = HtmlFormatter(full=False, linenos=True)
        html = '<style type="text/css">%s</style>' % formatter.get_style_defs()
        html += highlight(diff_text, DiffLexer(), formatter)

    return html


class PerFieldCompare(object):
    def __init__(self):
        pass

    def _make_html_diff(self, value1, value2):
        """
        TODO: Use diff_match_patch from above and ndiff as fallback
        """
        diff = difflib.ndiff(value1, value2)
        diff_text = "\n".join(diff)

        html = highlight_diff(diff_text)

        html = mark_safe(html)
        return html

    def __call__(self, obj, version1, version2):
        """
        Create a generic html diff from the obj between version1 and version2:
        
            A diff of every changes field values.
        
        This method should be overwritten, to create a nice diff view
        coordinated with the model.
        """
        diff = []

        for field in obj._meta.fields:
            #print field, field.db_type, field.get_internal_type()

            field_name = field.name
            value1 = version1.field_dict[field_name]
            value2 = version2.field_dict[field_name]

            if value1 == value2:
                # Skip all fields that aren't changed
                continue

            if isinstance(value1, basestring):
                value1 = value1.splitlines()
                value2 = value2.splitlines()
            else:
                # FIXME: How to create a better representation of the current value?
                value1 = [repr(value1)]
                value2 = [repr(value2)]

            html = self._make_html_diff(value1, value2)
            diff.append({
                "field_name": field_name,
                "diff": html
            })
        return diff


