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

MAXIMUM_RECOMMENDED_MODULES = 5
MINIMUM_ABSOLUTE_SIMILARITY = 0

# Create your views here.

# TODO: Adjust for new module_data
f = open('sungem/output.json')
module_data = json.load(f)
f.close()
similarity = np.genfromtxt('sungem/similarity.csv', delimiter=',')

# Create dict with subset of attributes for faster recommendation
relevant_attr = ['Angebotsturnus', 'Kreditpunkte', 'Modul Nr.', 'Moduldauer', 'Modulname', 'Sprache']
reduced_data = [dict(zip(relevant_attr, [d[att] for att in relevant_attr])) for d in module_data]

module_nr_map = {module['Modul Nr.']: module for module in module_data}


@api_view(['GET'])
def get_modules(request):
    """
    Returns compressed modules as json.
    """
    return http.JsonResponse(module_data, safe=False)


@api_view(['GET'])
def get_module(request, name=''):
    """
    Returns module as json.
    """
    return http.JsonResponse(module_nr_map[name], safe=False)


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
    """
    Returns Modules specifically recommended to certain user
    """

    # TODO: replace with actual user data
    # votes = {122: 5, 140: 5, 15: 5, 6: -5, 11: -5, 10: -1, 3: 3}

    votes = {vote.module: vote.score for vote in Vote.objects.filter(user=request.user)}

    # use only content based filtering to return recommended modules.
    # TODO: include community based filtering
    recommended = sorted(enumerate(reduced_data),
                         key=lambda e: sum(similarity[e[0], module] * score for module, score in votes.items()),
                         reverse=True)

    recommended = [r for r in recommended
                   if r[0] not in votes
                   and sum(similarity[r[0], module] * score
                           for module, score in votes.items()) > MINIMUM_ABSOLUTE_SIMILARITY]

    return response.Response(recommended[:MAXIMUM_RECOMMENDED_MODULES])


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
