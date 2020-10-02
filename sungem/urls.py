from django.urls import path

# for login
from rest_framework.authtoken import views as authviews

from . import views

urlpatterns = [
    path('recommend/', views.get_recommended_modules),
    path('vote/', views.vote),
    path('modules/', views.get_modules),
    path('module/<str:name>/', views.get_module),

    path('register/', views.register_user),
    path('login/', authviews.obtain_auth_token),
    path('logout/', views.logout_user),

    path('echo/', views.echo)

]
