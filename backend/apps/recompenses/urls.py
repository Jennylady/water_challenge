from django.urls import path
from .views import MesRecompensesView
urlpatterns = [
    path('mes-recompenses/',MesRecompensesView.as_view())
]
