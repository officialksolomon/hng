from rest_framework import serializers

from accounts.models import CustomUser
from api.models import Organisation

from api.models import Organisation


class CamelCaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {self.to_camel_case(key): value for key, value in ret.items()}

    def to_camel_case(self, snake_str):
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])


class UserSerializer(CamelCaseSerializer):
    class Meta:
        model = CustomUser
        fields = ["user_id", "first_name", "last_name", "email", "phone"]


class RegisterSerializer(CamelCaseSerializer):
    class Meta:
        model = CustomUser
        fields = ["user_id", "first_name", "last_name", "email", "password", "phone"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        organisation = Organisation.objects.create(
            name=f"{user.first_name}'s Organisation", description=""
        )
        organisation.users.set([user])
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class OrganisationSerializer(CamelCaseSerializer):
    class Meta:
        model = Organisation
        fields = ["org_id", "name", "description"]
