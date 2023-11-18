from rest_framework import serializers
from apps.education_plan.models import Invitations, Module, Card, Label


class InvitationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitations
        fields = ('tutor', 'student', 'invite_code', 'status', 'student_first_name', 'student_last_name')
        read_only_fields = ('tutor', 'student', 'invite_code')


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = (
            'id', 'title', 'description', 'date_start', 'date_end', 'plan_time', 'result_time', 'status', 'module',
            'labels')


class ModuleSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ('id', 'title', 'plan', 'cards')
