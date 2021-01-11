from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from register.models import CustomUser
from phonenumber_field.serializerfields import PhoneNumberField


class CustomUserSerializer(serializers.Serializer):

    LANGUAGES = [
        ('pl', 'pl'),
        ('eng', 'eng'),
    ]

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    telephone = PhoneNumberField(
        required=True,
        trim_whitespace=True,
        allow_blank=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    sms_notifications = serializers.BooleanField(default=False)
    app_notifications = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    language = serializers.ChoiceField(choices=LANGUAGES, required=True)

    def create(self, validated_data):
        """
        Create and return a new user instance, given the validated data.

        :param validated_data:
        :return: new user instance
        """
        if validated_data['password1'] != validated_data['password2']:
            raise serializers.ValidationError('Those passwords do not match')
        else:
            user = CustomUser.objects.create(username=validated_data.get('username'),
                                             email=validated_data.get('email'),
                                             password=validated_data.get('password1'),
                                             language=validated_data.get('language'),
                                             telephone=validated_data.get('telephone'))
            user.set_password(validated_data.get('password1'))
            user.save()
            return user


class DynamicUpdateCustomUserSerializer(serializers.ModelSerializer):
    """
    Class for creating dynamic fields in serializers
    """
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicUpdateCustomUserSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class UpdateCustomUserSerializer(DynamicUpdateCustomUserSerializer):

    LANGUAGES = [
        ('pl', 'pl'),
        ('eng', 'eng'),
    ]

    email = serializers.EmailField(required=False)
    telephone = PhoneNumberField(required=False, trim_whitespace=True, allow_blank=True)
    language = serializers.ChoiceField(choices=LANGUAGES, required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'telephone', 'sms_notifications', 'app_notifications', 'language']

    @staticmethod
    def validate_telephone(value):
        """
        Check if user with given phone number already exists in db

        """
        # If phone number is empty don't check in db
        if value != '':
            if CustomUser.objects.filter(telephone=value).exists():
                raise serializers.ValidationError('Telephone number already exists')

        return value

    @staticmethod
    def validate_email(value):
        """
        Check if user with given email already exists in db
        """""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email address already exists')
        return value

    def update(self, instance, validated_data):
        """
        Update and return an existing user instance, given the validated data.
        """
        instance.email = validated_data.get('email', instance.email)
        instance.telephone = validated_data.get('telephone', instance.telephone)
        instance.sms_notifications = validated_data.get('sms_notifications', instance.sms_notifications)
        instance.app_notifications = validated_data.get('app_notifications', instance.app_notifications)
        instance.language = validated_data.get('language', instance.language)
        instance.save()

        return instance


class CustomUserReadOnlySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    telephone = PhoneNumberField(read_only=True)
    sms_notifications = serializers.BooleanField(read_only=True)
    app_notifications = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    language = serializers.CharField(read_only=True)
