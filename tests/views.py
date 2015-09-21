
from reversion_compare.views import HistoryCompareDetailView
from .models import SimpleModel

class SimpleModelHistoryCompareView(HistoryCompareDetailView):
    model = SimpleModel
    