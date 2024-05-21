from rest_framework import serializers
from apps.education_plan.models import EducationPlan
from apps.schedule.models import Lesson


class LessonSerializerForTutorSerializer(serializers.ModelSerializer):
    discipline = serializers.CharField(source='education_plan.discipline', read_only=True)
    first_name = serializers.CharField(source='education_plan.student_first_name', read_only=True)
    last_name = serializers.CharField(source='education_plan.student_last_name', read_only=True)
    plan_id = serializers.CharField(write_only=True)

    class Meta:
        model = Lesson
        fields = ('id', 'date_start', 'date_end', 'discipline', 'first_name', 'last_name', 'plan_id', 'is_canceled')
        read_only_fields = ('id', 'discipline', 'first_name', 'last_name', 'is_canceled')

    def create(self, validated_data):
        plan_id = validated_data.pop('plan_id')
        plan = EducationPlan.objects.filter(id=plan_id, tutor=self.context['request'].user.userprofile).first()

        if not plan:
            raise serializers.ValidationError("Образовательный план не найден или не принадлежит вам.")

        validated_data['education_plan'] = plan
        instance = Lesson.objects.create(**validated_data)
        return instance


class LessonSerializerForStudentSerializer(serializers.ModelSerializer):
    discipline = serializers.CharField(source='education_plan.discipline', read_only=True)
    first_name = serializers.CharField(source='education_plan.tutor.first_name', read_only=True)
    last_name = serializers.CharField(source='education_plan.tutor.last_name', read_only=True)

    class Meta:
        model = Lesson
        fields = ('id', 'date_start', 'date_end', 'discipline', 'first_name', 'last_name', 'is_canceled')
        read_only_fields = ('id', 'date_start', 'date_end', 'discipline', 'first_name', 'last_name', 'is_canceled')
