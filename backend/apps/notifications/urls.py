from django.urls import path
from .views import MesNotificationsView, LireNotificationView, ToutMarquerLuView
urlpatterns=[path('',MesNotificationsView.as_view()),path('<int:notification_id>/lire/',LireNotificationView.as_view()),path('tout-lire/',ToutMarquerLuView.as_view())]
