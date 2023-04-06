from reversion_compare.views import HistoryCompareDetailView
from reversion_compare_project.models import SimpleModel


class SimpleModelHistoryCompareView(HistoryCompareDetailView):
    model = SimpleModel
