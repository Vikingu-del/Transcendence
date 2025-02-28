from django.urls import path
from .views import NotificationListView, NotificationMarkReadView

urlpatterns = [
    path('api/notification/', NotificationListView.as_view(), name='notification_list_view'),
    path('api/notification/mark-read/', NotificationMarkReadView.as_view(), name='mark_all_read'),
    path('api/notification/mark-read/<int:pk>/', NotificationMarkReadView.as_view(), name='mark_one_read'),
]