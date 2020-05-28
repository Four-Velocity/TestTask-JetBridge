from django.urls import path
from .views import *

urlpatterns = [
    path('', main),
    path('user_<int:pk>/', user_profile),
    path('user_<int:pk>/edit/', profile_edit),
    #
    path('login/', sign_in),
    path('logout/', log_out),
    path('register/', sign_up),
    path('register/<str:invited_with>/', sign_up),
]