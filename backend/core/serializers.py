from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    message = serializers.CharField()
