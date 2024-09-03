from rest_framework import serializers
from .models import Task, SubTask, Note
from generic_relations.relations import GenericRelatedField
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'priority', 'status', 'subtasks']
    
    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'content_type', 'object_id']
    
    def update(self, instance, validated_data):
        # Обработка обновления
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

    def validate(self, data):
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        if self.partial:
            note = self.instance
            content_type = note.content_type
            object_id = note.object_id
            data['content_object'] = self.add_content_object(content_type, object_id)
        elif content_type and object_id:
            data['content_object'] = self.add_content_object(content_type, object_id)
        else:
            raise serializers.ValidationError({"content_type": "This field is required", "object_id": "This field is required"})
        return data  
    
    def add_content_object(self, content_type, object_id):
        try:
            content_type_instance = ContentType.objects.get(model=content_type.model)
            content_object = content_type_instance.get_object_for_this_type(id=object_id)
            return content_object
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({"content_type": "Invalid content type"})
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"object_id": "Invalid object id"})
