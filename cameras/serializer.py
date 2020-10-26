from rest_framework import serializers
from cameras.models import Cameras


class CamerasSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=30, required=False)

    class Meta:
        model = Cameras
        fields = ['id', 'name',  'ip_address']

    @staticmethod
    def validate_name(value):
        """
        Check if camera with provided name exists in database.
        :param value:
        :return:
        """
        if Cameras.objects.filter(name=value).exists():
            raise serializers.ValidationError('Sensor with provided name already exists')
        return value

    def create(self, validated_data):
        """
        Create and return new camera instance, given the validated data
        :param validated_data:
        :return: new sensor instance
        """

        if not validated_data.get('name'):
            raise serializers.ValidationError('You need to provide name of the sensor')

        camera = Cameras.objects.create(name=validated_data.get('name'))
        camera.save()

        return camera

    def update(self, instance, validated_data):
        """
        Update and return an existing camera instance, given the validated data
        :param instance:
        :param validated_data:
        :return: updated sensor instance
        """
        instance.name = validated_data.get('name', instance.name)
        instance.ip_address = validated_data.get('ip_address', instance.ip_address)
        instance.save()

        return instance
