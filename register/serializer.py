from rest_framework import serializers
from register.models import CustomUser
from phonenumber_field.serializerfields import PhoneNumberField


class CustomUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    telephone = PhoneNumberField(required=True)
    sms_notifications = serializers.BooleanField(default=True)
    app_notifications = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.

        :param validated_data:
        :return: new user instance
        """
        if validated_data.get('password1') != validated_data.get('password2'):
            raise serializers.ValidationError('Those passwords do not match')
        else:
            return CustomUser.objects.create(username = validated_data.get('username'),
                                            email = validated_data.get('email'),
                                            password = validated_data.get('password1'),
                                            telephone = validated_data.get('telephone'))

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
