from rest_framework import serializers
from sensors.models import Sensors, SensorsData
from django.utils import timezone


class DynamicSensorsSerializer(serializers.ModelSerializer):
    """
    Class for creating dynamic fields in serializers
    """
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicSensorsSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class SensorsSerializer(DynamicSensorsSerializer):
    CATEGORIES = [
        ('temperature', 'temperature'),
        ('humidity', 'humidity'),
    ]

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30, required=False)
    category = serializers.ChoiceField(choices=CATEGORIES, required=False)
    # battery_level = serializers.IntegerField(default=None)
    # notifications = serializers.BooleanField(default=True)
    # is_active = serializers.BooleanField(default=True)

    class Meta:
        model = Sensors
        fields = ['id', 'name', 'category']

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

        if not validated_data.get('name') or not validated_data.get('category'):
            raise serializers.ValidationError('You need to provide name and category of sensor')

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

    sensor_id = serializers.SlugRelatedField(read_only=False, slug_field='id', queryset=Sensors.objects.all())
    delivery_time = serializers.DateTimeField(default=timezone.now)
    sensor_data = serializers.CharField(max_length=20)

    def create(self, validated_data):
        """
        Create instance of data collected by sensor.
        :param validated_data:
        :return:
        """
        data = SensorsData.objects.create(sensor_id=validated_data.get('sensor_id'),
                                                 sensor_data=validated_data.get('sensor_data'))
        return data

    def update(self, instance, validated_data):
        pass
