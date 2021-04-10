import json

import numpy as np
from django import http
from django.contrib.auth import models as authmodels
from rest_framework import response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated

from sungem.models import Vote
from sungem.recommender import recommend_modules, similar_modules, update_model

# Create your views here.

f = open('sungem/modules.json')
module_data = json.load(f)
f.close()
similarity = np.genfromtxt('sungem/similarity.csv', delimiter=',')

# Create dict with subset of attributes for faster recommendation
# TODO: Change this after better module file has been created. Maybe preprocess to better separate concerns.
relevant_attr = ['name', 'id', 'cp', 'duration', 'self_study', 'cycle', 'language']
reduced_data = [dict(zip(relevant_attr, [d[att] for att in relevant_attr])) for d in module_data]

module_nr_map = {module['id']: (module, index) for index, module in enumerate(module_data)}


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
    safe_name = name.replace('_', '/')
    if safe_name not in module_nr_map:
        return http.HttpResponseBadRequest('Incorrect module.')
    return http.JsonResponse(module_nr_map[safe_name][0], safe=False)


@api_view(['GET'])
def get_similar(request, module=''):
    """
    Returns similar modules to the given module.
    """
    safe_name = module.replace('_', '/')
    if safe_name not in module_nr_map:
        return http.HttpResponseBadRequest('Incorrect module.')
    return response.Response(similar_modules(5, module_nr_map[safe_name][1]))


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
    Returns recommended modules using a hybrid recommender system.
    """
    recommended_ids = recommend_modules(request.user, n=10)

    return response.Response([reduced_data[index] for index in recommended_ids])


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def vote(request):
    """
    Requires logged-in user, "module" and "score" attribute
    """

    if 'score' not in request.data or 'module' not in request.data:
        return http.HttpResponseBadRequest('Request needs to have score and module attribute.')

    if request.data['module'].replace('_', '/') not in module_nr_map:
        return http.HttpResponseBadRequest('Invalid module id: ' + request.data['module'].replace('_', '/') + ".")

    if request.data['score'] != 0:
        Vote.objects.update_or_create(
            user=request.user, module=request.data['module'].replace('_', '/'),
            defaults={'score': request.data['score']}
        )
    else:
        Vote.objects.filter(user=request.user).filter(module=request.data['module'].replace('_', '/')).delete()

    #update_model()  # TODO: consider removing this in favor of a more static and less computationally expensive approach

    return response.Response()


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_votes(request):
    """
    Get own votes.
    """
    # TODO: maybe reduce information sent back since most is only needed after choosing a module

    user_votes = Vote.objects.filter(user=request.user)
    return response.Response([(module_nr_map[vote.module][0], vote.score) for vote in user_votes])


@api_view(['POST'])
def update(request):
    """
    Api endpoint to force model recomputation in recommender engine. Currently not needed since model is recomputed
    after every vote.
    """
    update_model()
    return response.Response()
