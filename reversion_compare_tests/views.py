from reversion_compare.views import HistoryCompareDetailView

from reversion_compare_tests.models import SimpleModel


class SimpleModelHistoryCompareView(HistoryCompareDetailView):
    model = SimpleModel
