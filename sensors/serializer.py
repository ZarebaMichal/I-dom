from rest_framework import serializers
from sensors.models import Sensors, SensorsData


class DynamicSensorsSerializer(serializers.ModelSerializer):
    """
    Class for creating dynamic fields in serializers
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicSensorsSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class SensorsSerializer(DynamicSensorsSerializer):
    CATEGORIES = [
        ('temperature', 'temperature'),
        ('humidity', 'humidity'),
        ('smoke', 'smoke'),
        ('gas', 'gas'),
        ('water_temp', 'water_temp'),
        ('breathalyser', 'breathalyser'),
    ]

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30, required=False)
    category = serializers.ChoiceField(choices=CATEGORIES, required=False)
    last_data = serializers.SerializerMethodField()

    class Meta:
        model = Sensors
        fields = ['id', 'name', 'category', 'frequency', 'ip_address', 'last_data']

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

    @staticmethod
    def validate_frequency(value):
        """
        Check if given frequency is greater than 0 and less than int max value
        :param value:
        :return:
        """
        if value <= 0 or value >= 21474836:
            raise serializers.ValidationError('Frequency must be between 1 or 21474836')
        return value

    def get_last_data(self, obj):
        """
        Check for last data added for sensor
        :param obj:
        :return:
        """
        last_data = obj.sensorsdata_set.last()
        if last_data is not None:
            return last_data.sensor_data
        return None

    def create(self, validated_data):
        """
        Create and return new sensor instance, given the validated data
        :param validated_data:
        :return: new sensor instance
        """

        if not validated_data.get('name') or not validated_data.get('category') or not validated_data.get('frequency'):
            raise serializers.ValidationError('You need to provide name, category and frequency of sensor')

        sensor = Sensors.objects.create(name=validated_data.get('name'),
                                        category=validated_data.get('category'),
                                        frequency=validated_data.get('frequency')
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
        instance.frequency = validated_data.get('frequency', instance.frequency)
        instance.ip_address = validated_data.get('ip_address', instance.ip_address)
        instance.save()

        return instance


class SensorsDataSerializer(serializers.ModelSerializer):
    sensor = serializers.SlugRelatedField(read_only=False, many=False, slug_field='name', queryset=Sensors.objects.all())

    class Meta:
        model = SensorsData
        fields = ("sensor", "delivery_time", "sensor_data")
