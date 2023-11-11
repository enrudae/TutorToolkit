from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from rest_framework import serializers


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)

    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('email', 'password', 'role', 'first_name', 'last_name')

    def get_fields(self):
        fields = super(UserRegistrationSerializer, self).get_fields()

        role = self.initial_data.get('role')
        if role == 'tutor':
            fields['first_name'].required = True
            fields['last_name'].required = True

        return fields
