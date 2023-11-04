from rest_framework import serializers

from apps.education_plan.models import EducationPlan


class EducationPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = EducationPlan
        fields = ('title', 'tutor', 'student', 'invite_code', 'status')
        read_only_fields = ('tutor', 'student', 'invite_code')

