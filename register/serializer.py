from rest_framework import serializers
from register.models import CustomUser


class CustomUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(unique=True)
    telephone = serializers.CharField(unique=True)
    sms_notifications = serializers.BooleanField(default=True)
    app_notifications = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.

        :param validated_data:
        :return: new user instance
        """

        return CustomUser.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing user instance, given the validated data.

        :param instance:
        :param validated_data:
        :return: updated user instance
        """

        instance.email = validated_data.get('email', instance.email)
        instance.telephone = validated_data.get('telephone', instance.telephone)
        instance.sms_notifications = validated_data.get('sms_notifications', instance.sms_notifications)
        instance.app_notifications = validated_data.get('app_notifications', instance.app_notifications)
        instance.save()

        return instance
