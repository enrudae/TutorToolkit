from rest_framework import serializers
from apps.education_plan.models import EducationPlan, Module, Card, Label
from apps.account.serializers import TutorSerializer


class EducationPlanSerializer(serializers.ModelSerializer):
    tutor = TutorSerializer(read_only=True)

    class Meta:
        model = EducationPlan
        fields = ('id', 'tutor', 'invite_code', 'status', 'student_first_name', 'student_last_name')
        read_only_fields = ('id', 'tutor', 'invite_code')


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
        read_only_fields = ('id',)


class ModuleSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ('id', 'title', 'plan', 'cards')
        read_only_fields = ('id', 'plan')


class ModulesInEducationPlanSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    class Meta:
        model = EducationPlan
        fields = ('modules',)
        read_only_fields = ('modules',)
