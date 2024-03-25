from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from rest_framework import serializers
from apps.account.models import UserProfile


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    first_name = serializers.CharField(required=False, help_text='Required for tutor role')
    last_name = serializers.CharField(required=False, help_text='Required for tutor role')
    invite_code = serializers.CharField(required=False, help_text='Required for student role')
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, write_only=True)

    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('email', 'password', 'role', 'first_name', 'last_name', 'invite_code')

    def validate(self, data):
        role = data.get('role')
        if role == 'tutor' and ('first_name' not in data or 'last_name' not in data):
            raise serializers.ValidationError("First name and last name are required for tutor role")
        if role == 'student' and 'invite_code' not in data:
            raise serializers.ValidationError("Invite_code are required for student role")
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'first_name', 'last_name', 'role')
        read_only_fields = ('id', 'role')
