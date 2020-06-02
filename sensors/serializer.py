from rest_framework import serializers
from sensors.models import Sensors, SensorsData
from django.utils import timezone


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

    @staticmethod
    def validate_name(value):
        """
        Check if sensor with provided name exists in database.
        :param value:
        :return:
        """
        if Sensors.objects.filter(name=value).exists():
            raise serializers.ValidationError('Sensor with provided name already exists')
        return value

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


class SensorsDataSerializer(serializers.Serializer):

    sensor_id = serializers.ReadOnlyField(source=Sensors.id)
    delivery_time = serializers.DateTimeField(default=timezone.now)
    sensor_data = serializers.CharField(max_length=20)

    def create(self, validated_data):
        """
        Create instance of data collected by sensor.
        :param validated_data:
        :return:
        """
        sensor_data = SensorsData.oobjects.create(
                                                  sensor_data=validated_data.get('sensor_data')
                                                  )
        return sensor_data

    def update(self, instance, validated_data):
        pass
