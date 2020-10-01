from django.shortcuts import render
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from django import http

import json

from rest_framework.authtoken import views as authviews
from django.contrib.auth import models as authmodels


# Create your views here.


@api_view(['GET'])
def get_modules(request):
    """
    Returns compressed modules as json.
    """
    f = open('sungem/output.json')
    data = json.load(f)
    f.close()
    return http.JsonResponse(data, safe=False)


@api_view(['POST'])
def register_user(request):
    """
    Registers a user if they don't exist yet. Does NOT log the user in.
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
    Test Endpoint
    """
    return response.Response(request.user.username)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_recommended_modules(request):
    """
    Returns Modules specifically recommended to certain user
    """
    return response.Response(request.body['username'])
    # if request.user.is_authenticated:
    #    return Response("Hello There.")
    # else:
    #    return Response("General Kenobi.")
