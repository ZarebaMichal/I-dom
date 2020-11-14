from rest_framework import serializers
from driver.models import Drivers


class DynamicDriversSerializer(serializers.ModelSerializer):
    """
    Class for creating dynamic fields in serializers
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicDriversSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class DriversSerializer(DynamicDriversSerializer):
    CATEGORIES = [
        ('remote_control', 'remote_control'),
        ('roller_blind', 'roller_blind'),
        ('clicker', 'clicker'),
        ('bulb', 'bulb'),
    ]

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30, required=False)
    category = serializers.ChoiceField(choices=CATEGORIES, required=False)
    data = serializers.BooleanField(allow_null=True)

    class Meta:
        model = Drivers
        fields = ['id', 'name', 'category', 'ip_address', 'data']

    def create(self, validated_data):
        """
        Create and return new driver instance, given the validated data
        :param validated_data:
        :return: new driver instance
        """

        if not validated_data.get('name') or not validated_data.get('category'):
            raise serializers.ValidationError('You need to provide name and category of driver')

        driver = Drivers.objects.create(name=validated_data.get('name'),
                                        category=validated_data.get('category'),
                                        data=validated_data.get('data')
                                        )
        driver.save()
        return driver

    def update(self, instance, validated_data):
        """
        Update and return an existing driver instance, given the validated data
        :param instance:
        :param validated_data:
        :return: updated driver instance
        """
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.ip_address = validated_data.get('ip_address', instance.ip_address)
        instance.data = validated_data.get('data', instance.data)
        instance.save()

        return instance

    @staticmethod
    def validate_name(value):
        """
        Check if driver with provided name exists in database.
        :param value:
        :return:
        """
        if Drivers.objects.filter(name=value).exists():
            raise serializers.ValidationError('Driver with provided name already exists')
        return value
