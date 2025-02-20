"""
URL configuration for userService project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from .views import (
    ProfileView, SearchProfilesView, AddFriendView,
    RemoveFriendView, AcceptFriendRequestView, DeclineFriendRequestView,
    IncomingFriendRequestsView, BlockUserView, SyncTokenView, UpdateOnlineStatusView
)

urlpatterns = [
    # Sync token endpoint
    path('api/user/sync-token/', SyncTokenView.as_view(), name='sync-token'),
    
    # Profile endpoints
    path('api/user/profile/', ProfileView.as_view(), name='profile'),
    path('api/user/profile/search/', SearchProfilesView.as_view(), name='search_profiles'),
    
    # Friend management endpoints
    path('api/user/profile/add_friend/', AddFriendView.as_view(), name='add_friend'),
    path('api/user/profile/remove_friend/', RemoveFriendView.as_view(), name='remove_friend'),
    path('api/user/profile/friend-requests/', IncomingFriendRequestsView.as_view(), name='friend_requests'),
    path('api/user/profile/friend-requests/accept/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('api/user/profile/friend-requests/decline/', DeclineFriendRequestView.as_view(), name='decline_friend_request'),

    # Block management endpoints
    path('api/user/profile/<int:user_id>/block/', BlockUserView.as_view(), name='block-user'),

    # Online Status
    path('api/user/profile/online-status/', UpdateOnlineStatusView.as_view(), name='online-status'),

    # Media files
    re_path(r'^api/user/media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
        'show_indexes': False,
    }),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)