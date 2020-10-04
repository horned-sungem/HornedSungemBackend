from rest_framework import serializers
from sungem.models import Vote


class VoteSerializer(serializers.ModelSerializer):
    # TODO: evaluate if this class is needed. Vote serializers are not used anymore
    class Meta:
        model = Vote
        fields = ['user', 'module', 'score']
