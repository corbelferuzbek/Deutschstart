from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from .models import StudentProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    grade = serializers.ChoiceField(
        choices=StudentProfile.Grade.choices,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "grade"
        ]

    @transaction.atomic
    def create(self, validated_data):
        grade = validated_data.pop("grade")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            role=User.Role.STUDENT,
            **validated_data
        )

        StudentProfile.objects.create(
            user=user,
            grade=grade
        )

        return user