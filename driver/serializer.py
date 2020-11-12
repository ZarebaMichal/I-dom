from rest_framework import serializers
from driver.models import Drivers


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


class DriversSerializer(DynamicSensorsSerializer):
    CATEGORIES = [
        ('remote_control', 'remote_control'),
        ('roller_blind', 'roller_blind'),
        ('clicker', 'clicker'),
        ('bulb', 'bulb'),
    ]

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30, required=False)
    category = serializers.CharField(max_length=15, choices=CATEGORIES)
    data = serializers.BooleanField(null=True)

    class Meta:
        model = Drivers
        fields = ['id', 'name', 'category', 'ip_address', 'data']
