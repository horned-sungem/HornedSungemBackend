from django.urls import path

# for login
from rest_framework.authtoken import views as authviews

from . import views

urlpatterns = [
    path('recommend/', views.get_recommended_modules),  # Get recommended modules
    path('vote/', views.vote),  # Submit a vote
    path('votes/', views.get_votes),  # Get your votes
    path('modules/', views.get_modules),  # Get all modules (reduced)
    path('module/<str:name>/', views.get_module),  # Get a certain module
    path('similar/<str:module>/', views.get_similar),  # Get similar modules

    path('register/', views.register_user),  # register a user
    path('login/', authviews.obtain_auth_token),  # login a user
    path('logout/', views.logout_user),  # logout a user

    path('echo/', views.echo),  # echo if user is authenticated
    # path('update/', views.update)  # update the internal model
]
