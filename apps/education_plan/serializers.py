from rest_framework import serializers
from apps.education_plan.models import EducationPlan, Invitations


class InvitationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invitations
        fields = ('tutor', 'student', 'invite_code', 'status', 'student_first_name', 'student_last_name')
        read_only_fields = ('tutor', 'student', 'invite_code')


class EducationPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = EducationPlan
        fields = ('title',)
