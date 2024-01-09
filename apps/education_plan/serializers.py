from rest_framework import serializers
from apps.education_plan.models import EducationPlan, Module, Card, Label
from apps.account.serializers import TutorSerializer


class EducationPlanSerializer(serializers.ModelSerializer):
    tutor = TutorSerializer(read_only=True)

    class Meta:
        model = EducationPlan
        fields = ('id', 'tutor', 'invite_code', 'status', 'discipline', 'student_first_name', 'student_last_name')
        read_only_fields = ('id', 'tutor', 'invite_code')


class EducationPlanForStudentSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = EducationPlan
        fields = ('id', 'status', 'discipline', 'first_name', 'last_name')
        read_only_fields = ('id', )

    def get_first_name(self, obj):
        return obj.tutor.first_name if obj.tutor else None

    def get_last_name(self, obj):
        return obj.tutor.last_name if obj.tutor else None


class EducationPlanForTutorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='student_first_name', read_only=True)
    last_name = serializers.CharField(source='student_last_name', read_only=True)

    class Meta:
        model = EducationPlan
        fields = ('id', 'status', 'discipline', 'first_name', 'last_name')
        read_only_fields = ('id', )


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
