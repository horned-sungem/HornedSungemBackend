from django.urls import path

# for login
from rest_framework.authtoken import views as authviews

from . import views

urlpatterns = [
    path('sungem/', views.get_recommended_modules),
    path('modules/', views.get_modules),
    path('login/', authviews.obtain_auth_token),
    path('logout/', views.logout_user),
    path('register/', views.register_user),
    path('echo/', views.echo),
    path('vote/', views.vote)
]
