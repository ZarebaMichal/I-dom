from rest_framework import serializers
from sensors.models import Sensors


class SensorsSerializer(serializers.Serializer):
    CATEGORIES = [
        ('temperature', 'temperature'),
        ('humidity', 'humidity'),
    ]

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30)
    category = serializers.ChoiceField(choices=CATEGORIES)
    battery_level = serializers.IntegerField(default=None)
    notifications = serializers.BooleanField(default=True)
    is_active = serializers.BooleanField(default=True)

    def create(self, validated_data):
        """
        Create and return new sensor instance, given the validated data
        :param validated_data:
        :return: new sensor instance
        """
        sensor = Sensors.objects.create(name=validated_data.get('name'),
                                        category=validated_data.get('category'),
                                        )
        sensor.save()
        return sensor

    def update(self, instance, validated_data):
        """
        Update and return an existing sensor instance, given the validated data
        :param instance:
        :param validated_data:
        :return: updated sensor instance
        """
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.save()

        return instance
