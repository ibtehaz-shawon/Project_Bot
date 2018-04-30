from rest_framework import serializers
from .models import DataDump, UserTable, DonationHistory, ErrorLog, UserStatus


class DumpMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDump
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTable
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
        model = ErrorLog
        fields = '__all__'
