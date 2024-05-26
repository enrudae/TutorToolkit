from rest_framework import serializers
from django.shortcuts import get_object_or_404
from apps.education_plan.models import EducationPlan, Module, Card, Label, File, CardContent, SectionContent
from apps.account.serializers import ProfileSerializer
from TutorToolkit.constants import FILE_RESTRICTIONS


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
    card_id = serializers.UUIDField(required=False, write_only=True)

    class Meta:
        model = Label
        fields = ('id', 'title', 'color', 'card_id')
        read_only_fields = ('id',)

    def create(self, validated_data):
        card_id = validated_data.pop('card_id', None)
        label = Label.objects.create(**validated_data)
        if card_id:
            card = get_object_or_404(Card, pk=card_id)
            card.labels.add(label)
        return label


class CardSerializer(serializers.ModelSerializer):
    module_id = serializers.CharField(write_only=True)
    labels = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all(), many=True, write_only=True)

    class Meta:
        model = Card
        fields = (
            'id', 'title', 'description', 'date_start', 'date_end', 'plan_time', 'result_time', 'repetition_date',
            'status', 'module', 'labels', 'module_id', 'index', 'difficulty')
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
        fields = ('id', 'title', 'plan', 'cards', 'plan_id', 'index')
        read_only_fields = ('id', 'plan', 'index')


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


class FileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)

    class Meta:
        model = File
        fields = ('id', 'file', 'name', 'extension', 'size', 'upload_date', 'tutor')
        read_only_fields = ('id', 'extension', 'size', 'upload_date', 'tutor')

    def validate(self, data):
        file = data.get('file')
        if file:
            name = file.name
            extension = name.split('.')[-1].lower()
            size = file.size

            if extension not in FILE_RESTRICTIONS:
                raise serializers.ValidationError({
                    'file': [f"Файл с расширением {extension} не разрешен."],
                    'name': name
                })

            max_size = FILE_RESTRICTIONS[extension]['max_size']
            if size > max_size:
                max_size_mb = max_size / 1024 / 1024
                raise serializers.ValidationError({
                    'file': [f"Размер файла {extension} должен быть менее {max_size_mb} MB."],
                    'name': name
                })

            data['extension'] = extension
            data['size'] = size

        return data


class SectionContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionContent
        fields = ('id', 'text', 'files',)
        read_only_fields = ('id',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['files'] = FileSerializer(instance.files.all(), many=True).data
        return representation


class CardContentSerializer(serializers.ModelSerializer):
    card_id = serializers.CharField(write_only=True)
    homework = SectionContentSerializer(required=False, allow_null=True)
    lesson = SectionContentSerializer(required=False, allow_null=True)
    repetition = SectionContentSerializer(required=False, allow_null=True)

    class Meta:
        model = CardContent
        fields = ('homework', 'lesson', 'repetition', 'card', 'card_id')
        read_only_fields = ('card',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['homework'] = SectionContentSerializer(instance.homework).data
        representation['lesson'] = SectionContentSerializer(instance.lesson).data
        representation['repetition'] = SectionContentSerializer(instance.repetition).data
        representation['card_title'] = instance.card.title
        return representation
