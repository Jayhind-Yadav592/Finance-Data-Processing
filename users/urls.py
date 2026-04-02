from django.urls import path
from .views import (
    RegisterView, LoginView, MeView,
    UserListView, UpdateUserRoleView, UpdateUserStatusView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(),  name='register'),
    path('login/',    LoginView.as_view(),      name='login'),
    path('me/',       MeView.as_view(),         name='me'),
]

# Admin-only user management
from django.urls import path
user_urlpatterns = [
    path('users/',              UserListView.as_view(),       name='user-list'),
    path('users/<int:pk>/role/',   UpdateUserRoleView.as_view(),   name='update-role'),
    path('users/<int:pk>/status/', UpdateUserStatusView.as_view(), name='update-status'),
]

urlpatterns += user_urlpatterns