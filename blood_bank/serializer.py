from rest_framework import serializers
from .models import *


class DumpMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDump
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInformation
        fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationHistory
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = '__all__'


class LoggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLogger
        fields = '__all__'


class FlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowController
        fields = '__all__'