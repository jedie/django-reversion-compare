from django.views.generic.detail import DetailView
from reversion.models import Version

from reversion_compare.mixins import CompareMethodsMixin, CompareMixin


class HistoryCompareDetailView(CompareMixin, CompareMethodsMixin, DetailView):
    """
    This class can be used to add a non-admin view for comparing your object's versions.
    You can use it just like a normal DetailView:

    Inherit from it in your class and add a model (or queryset), see:

        reversion_compare_project/views.py

    and assign your HistoryCompareDetailView to a url, see:

        reversion_compare_project/urls.py

    Last step, you need to create a template to display both the version select form and
    the changes part (if the form is submitted). and include some partials templates.
    An example template can be found here:

        reversion_compare_project/templates/reversion_compare_project/simplemodel_detail.html

    If you want more control on the appearence of your templates you can check these partials
    to understand how the available context variables are used.

    Note: The "make run-test-server" test project contains a Demo, use the links under:
        "HistoryCompareDetailView Examples:"
    """

    def _get_action_list(self):
        action_list = [
            {"version": version, "revision": version.revision}
            for version in self._order_version_queryset(
                Version.objects.get_for_object(self.get_object()).select_related("revision__user")
            )
        ]
        return action_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
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
            obj = self.get_object()
            queryset = Version.objects.get_for_object(obj)
            nav = self._resolve_versions_and_navigation(self.request.GET, queryset)
            version1 = nav['version1']
            version2 = nav['version2']

            compare_data, has_unfollowed_fields = self.compare(obj, version1, version2)

            context.update({
                'compare_data': compare_data,
                'has_unfollowed_fields': has_unfollowed_fields,
            })
            context.update(nav)  # merges version1, version2, next_url, prev_url

        # Compile the context.
        context.update({"action_list": action_list, "comparable": comparable, "compare_view": True})
        return context
