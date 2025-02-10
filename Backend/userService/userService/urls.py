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
from .views import (
    RegisterView, LoginView, ProfileView, LogoutView, SearchProfilesView,
    AddFriendView, RemoveFriendView, AcceptFriendRequestView,
    DeclineFriendRequestView, IncomingFriendRequestsView,
    BlockUserView
)


urlpatterns = [
    # Auth endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    
    # Profile endpoints
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/profile/search/', SearchProfilesView.as_view(), name='search_profiles'),
    
    # Friend management endpoints
    path('api/profile/add_friend/', AddFriendView.as_view(), name='add_friend'),
    path('api/profile/remove_friend/', RemoveFriendView.as_view(), name='remove_friend'),
    path('api/profile/friend-requests/', IncomingFriendRequestsView.as_view(), name='friend_requests'),
    path('api/profile/friend-requests/accept/', AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('api/profile/friend-requests/decline/', DeclineFriendRequestView.as_view(), name='decline_friend_request'),

    # Block management endpoints
    path('api/profile/<int:user_id>/block/', BlockUserView.as_view(), name='block-user'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)