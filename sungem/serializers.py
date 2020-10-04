from rest_framework import serializers
from sungem.models import Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['user', 'module', 'score']
