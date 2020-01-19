from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView

from reversion.models import Version

from reversion_compare.forms import SelectDiffForm
from reversion_compare.mixins import CompareMixin, CompareMethodsMixin


class HistoryCompareDetailView(CompareMixin, CompareMethodsMixin, DetailView):
    """This class can be used to add a non-admin view for comparing your object's versions.
    
    You can use it just like a normal DetailView:
    
    Inherit from it in your class and add a model (or queryset), for example:
    
    class SimpleModelHistoryCompareView(HistoryCompareDetailView):
        model = SimpleModel
        
    and assign that CBV to a url: 
    
    url(r'^test_view/(?P<pk>\d+)$', views.SimpleModelHistoryCompareView.as_view() ),
    
    Last step, you need to create a template to display both the version select form and 
    the changes part (if the form is submitted). An example template is the following:
    
    <style type="text/css">
    /* minimal style for the diffs */
    del, ins {
        color: #000;
        text-decoration: none;
    }
    del { background-color: #ffe6e6; }
    ins { background-color: #e6ffe6; }
    sup.follow { color: #5555ff; }
    </style>


    {% include "reversion-compare/action_list_partial.html"  %}
    {% include "reversion-compare/compare_partial.html"  %}
    {% include "reversion-compare/compare_links_partial.html"  %}

    
    Beyond the styling, you should include 
    - reversion-compare/action_list_partial.html partial template to display the version select form
    - reversion-compare/compare_partial.html partial template to display the actual version
    - reversion-compare/compare_links_partial.html to include previous/next comparison links
    
    If you want more control on the appearence of your templates you can check these partials
    to understand how the availabble context variables are used.
    """

    def _get_action_list(self,):
        action_list = [
            {"version": version, "revision": version.revision}
            for version in self._order_version_queryset(
                Version.objects.get_for_object(self.get_object()).select_related("revision__user")
            )
        ]
        return action_list

    def get_context_data(self, **kwargs):
        context = super(HistoryCompareDetailView, self).get_context_data()
        action_list = self._get_action_list()

        if len(action_list) < 2:
            # Less than two history items aren't enough to compare ;)
            comparable = False
        else:
            comparable = True
            # for pre selecting the compare radio buttons depend on the ordering:
            if self.history_latest_first:
                action_list[0]["first"] = True
                action_list[1]["second"] = True
            else:
                action_list[-1]["first"] = True
                action_list[-2]["second"] = True

        if self.request.GET:
            form = SelectDiffForm(self.request.GET)
            if not form.is_valid():
                msg = "Wrong version IDs."
                raise Http404(msg)

            version_id1 = form.cleaned_data["version_id1"]
            version_id2 = form.cleaned_data["version_id2"]

            if version_id1 > version_id2:
                # Compare always the newest one (#2) with the older one (#1)
                version_id1, version_id2 = version_id2, version_id1

            obj = self.get_object()
            queryset = Version.objects.get_for_object(obj)
            version1 = get_object_or_404(queryset, pk=version_id1)
            version2 = get_object_or_404(queryset, pk=version_id2)

            next_version = queryset.filter(pk__gt=version_id2).last()
            prev_version = queryset.filter(pk__lt=version_id1).first()

            compare_data, has_unfollowed_fields = self.compare(obj, version1, version2)

            context.update(
                {
                    "compare_data": compare_data,
                    "has_unfollowed_fields": has_unfollowed_fields,
                    "version1": version1,
                    "version2": version2,
                }
            )

            if next_version:
                next_url = f"?version_id1={version2.id:d}&version_id2={next_version.id:d}"
                context.update({"next_url": next_url})
            if prev_version:
                prev_url = f"?version_id1={prev_version.id:d}&version_id2={version1.id:d}"
                context.update({"prev_url": prev_url})

        # Compile the context.
        context.update({"action_list": action_list, "comparable": comparable, "compare_view": True})
        return context
