from rest_framework import serializers
from apps.education_plan.models import EducationPlan, Module, Card, Label
from apps.account.serializers import ProfileSerializer


class EducationPlanSerializer(serializers.ModelSerializer):
    tutor = ProfileSerializer(read_only=True)

    class Meta:
        model = EducationPlan
        fields = ('id', 'tutor', 'invite_code', 'status', 'discipline', 'student_first_name', 'student_last_name')
        read_only_fields = ('id', 'tutor', 'invite_code')


class EducationPlanForStudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='tutor.first_name', read_only=True)
    last_name = serializers.CharField(source='tutor.last_name', read_only=True)

    class Meta:
        model = EducationPlan
        fields = ('id', 'status', 'discipline', 'first_name', 'last_name')
        read_only_fields = ('id', 'first_name', 'last_name')


class EducationPlanForTutorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='student_first_name', read_only=True)
    last_name = serializers.CharField(source='student_last_name', read_only=True)
    email = serializers.EmailField(source='student.user.email', read_only=True)

    class Meta:
        model = EducationPlan
        fields = ('id', 'status', 'discipline', 'first_name', 'last_name', 'email')
        read_only_fields = ('id', 'first_name', 'last_name', 'email')


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'title', 'color')
        read_only_fields = ('id',)


class CardSerializer(serializers.ModelSerializer):
    module_id = serializers.CharField(write_only=True)
    labels = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(), many=True, write_only=True)

    class Meta:
        model = Card
        fields = (
            'id', 'title', 'description', 'date_start', 'date_end', 'plan_time', 'result_time', 'status', 'module',
            'labels', 'module_id', 'index', 'difficulty')
        read_only_fields = ('id', 'module', 'index')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['labels'] = LabelSerializer(instance.labels.all(), many=True).data
        return representation


class ModuleSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    plan_id = serializers.CharField(write_only=True)

    class Meta:
        model = Module
        fields = ('id', 'title', 'plan', 'cards', 'plan_id')
        read_only_fields = ('id', 'plan')


class ModulesInEducationPlanSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = EducationPlan
        fields = ('id', 'discipline', 'modules',)
        read_only_fields = ('modules',)


class MoveElementSerializer(serializers.Serializer):
    ELEMENT_TYPES = ('task', 'board')

    element_type = serializers.ChoiceField(choices=ELEMENT_TYPES)
    element_id = serializers.CharField()
    destination_index = serializers.IntegerField()
    destination_id = serializers.CharField(required=False)

    def validate(self, data):
        element_type = data.get('element_type')
        destination_id = data.get('destination_id')

        if element_type == 'task' and destination_id is None:
            raise serializers.ValidationError("Field 'destination_id' is required for task.")

        return data
