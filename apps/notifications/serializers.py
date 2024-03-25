from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'text', 'content', 'date', 'is_active', 'type', 'education_plan')
        # read_only_fields = '__all__'
