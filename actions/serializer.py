from rest_framework import serializers
from driver.models import Drivers
from sensors.models import Sensors
from actions.models import Actions


class DynamicActionsSerializer(serializers.ModelSerializer):
    """
    Class for creating dynamic fields in serializers
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicActionsSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ActionsSerializer(DynamicActionsSerializer):

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50, required=False)
    sensor = serializers.SlugRelatedField(read_only=False, many=False, slug_field='name',
                                          queryset=Sensors.objects.all(), allow_null=True,
                                          required=False)
    trigger = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True, required=False)
    operator = serializers.CharField(max_length=1, allow_null=True, required=False)
    driver = serializers.SlugRelatedField(read_only=False, many=False, slug_field='name',
                                          queryset=Drivers.objects.all(), required=False)
    is_active = serializers.BooleanField(default=True)
    days = serializers.CharField(max_length=250, required=False)
    start_event = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'], required=False)
    end_event = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'], allow_null=True, required=False)
    action = serializers.CharField(max_length=50, required=False)
    flag = serializers.IntegerField(required=False)

    class Meta:
        model = Actions
        fields = ['id', 'name', 'sensor', 'trigger', 'operator', 'driver', 'is_active', 'days', 'start_event',
                  'end_event', 'action', 'flag']

    @staticmethod
    def validate_name(value):
        """
        Check if action with provided name exists in database.
        :param value:
        :return:
        """
        if Actions.objects.filter(name=value).exists():
            raise serializers.ValidationError('Action with provided name already exists')
        return value

    def create(self, validated_data):
        """
        Create and return new action instance, given the validated data
        :param validated_data:
        :return: new action instance
        """

        action = Actions.objects.create(name=validated_data.get('name'),
                                        sensor=validated_data.get('sensor'),
                                        trigger=validated_data.get('trigger'),
                                        operator=validated_data.get('operator'),
                                        driver=validated_data.get('driver'),
                                        days=validated_data.get('days'),
                                        start_event=validated_data.get('start_event'),
                                        end_event=validated_data.get('end_event'),
                                        action=validated_data.get('action'),
                                        flag=validated_data.get('flag')
                                        )
        action.save()
        return action

    def update(self, instance, validated_data):
        """
        Update and return an existing action instance, given the validated data
        :param instance:
        :param validated_data:
        :return: updated action instance
        """
        instance.name = validated_data.get('name', instance.name)
        instance.sensor = validated_data.get('sensor', instance.sensor)
        instance.trigger = validated_data.get('trigger', instance.trigger)
        instance.operator = validated_data.get('operator', instance.operator)
        instance.driver = validated_data.get('driver', instance.driver)
        instance.days = validated_data.get('days', instance.days)
        instance.start_event = validated_data.get('start_event', instance.start_event)
        instance.end_event = validated_data.get('end_event', instance.end_event)
        instance.action = validated_data.get('action', instance.action)
        instance.flag = validated_data.get('flag', instance.flag)
        instance.save()

        return instance
