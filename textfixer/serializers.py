# textfixer/serializers.py
from rest_framework import serializers

class TextRequestSerializer(serializers.Serializer):
    text = serializers.CharField()
    folder = serializers.CharField(required=False, allow_blank=True)
    filename = serializers.CharField(required=False, allow_blank=True)

class TextResponseSerializer(serializers.Serializer):
    text = serializers.CharField()
