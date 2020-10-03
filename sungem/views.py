from django.shortcuts import render
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from django import http

import json
import numpy as np

from rest_framework.authtoken import views as authviews
from django.contrib.auth import models as authmodels

from .models import Vote

from .recommender import *

# Create your views here.

# TODO: Adjust for new module_data
f = open('sungem/output.json')
module_data = json.load(f)
f.close()
similarity = np.genfromtxt('sungem/similarity.csv', delimiter=',')

# Create dict with subset of attributes for faster recommendation
relevant_attr = ['Angebotsturnus', 'Kreditpunkte', 'Modul Nr.', 'Moduldauer', 'Modulname', 'Sprache']
reduced_data = [dict(zip(relevant_attr, [d[att] for att in relevant_attr])) for d in module_data]

module_nr_map = {module['Modul Nr.']: (module, index) for index, module in enumerate(module_data)}


@api_view(['GET'])
def get_modules(request):
    """
    Returns compressed modules as json.
    """
    return http.JsonResponse(reduced_data, safe=False)


@api_view(['GET'])
def get_module(request, name=''):
    """
    Returns module as json.
    """
    return http.JsonResponse(module_nr_map[name.replace('_', '/')][0], safe=False)


@api_view(['POST'])
def register_user(request):
    """
    Registers a user if they don't exist yet. Does NOT log the user in.
    Requires "username" and "password" attributes.
    """
    data = request.data
    if 'username' not in data or 'password' not in data:
        return http.HttpResponseBadRequest("username and password field required.")
    users = authmodels.User.objects.filter(username=data['username'])
    if users:
        return http.HttpResponseBadRequest('Username already exists')
    authmodels.User.objects.create_user(data['username'], password=data['password'])
    return response.Response()


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout user by deleting their unique token.
    """
    request.user.auth_token.delete()
    return response.Response()


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def echo(request):
    """
    Authentication Test Endpoint
    """
    return response.Response('user ' + request.user.username + ' is authenticated.')


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_recommended_modules(request):
    recommended_ids = recommend_modules(request.user)

    return response.Response([reduced_data[index] for index in recommended_ids])


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def vote(request):
    """
    "Requires logged-in user, "module" and "score" attribute
    """

    if 'score' not in request.data or 'module' not in request.data:
        return http.HttpResponseBadRequest('Request needs to have score and module attribute.')

    if request.data['score'] != '0':
        Vote.objects.update_or_create(
            user=request.user, module=request.data['module'],
            defaults={'score': request.data['score']}
        )
    else:
        Vote.objects.filter(user=request.user).filter(module=request.data['module']).delete()

    return response.Response()


@api_view(['POST'])
def update(request):
    update_model()
    return response.Response()
