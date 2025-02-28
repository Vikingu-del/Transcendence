# In your notificationService/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/notification/', views.NotificationListView.as_view(), name='notification-list'),
    path('api/notification/unread-count/', views.NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('api/notification/<int:notification_id>/read/', views.NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('api/notification/read-all/', views.NotificationMarkReadView.as_view(), name='notifications-mark-all-read'),
]