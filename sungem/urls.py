from django.urls import path

# for login
from rest_framework.authtoken import views as authviews

from . import views

import re

urlpatterns = [
    path('recommend/', views.get_recommended_modules),
    path('vote/', views.vote),
    path('votes/', views.get_votes),
    path('modules/', views.get_modules),
    path('module/<str:name>/', views.get_module),
    path('similar/<str:module>/', views.get_similar),

    path('register/', views.register_user),
    path('login/', authviews.obtain_auth_token),
    path('logout/', views.logout_user),

    path('echo/', views.echo),
    path('update/', views.update)
]
