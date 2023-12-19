"""
URL mapping for the users API
"""
from django.urls import path

from user.views import CreateUserView, CreateAuthTokenView, ManageUserView

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('token/', CreateAuthTokenView.as_view(), name='token'),
    path('me/', ManageUserView.as_view(), name='me'),
]
