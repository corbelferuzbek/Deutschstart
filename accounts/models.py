from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class StudentProfile(models.Model):

    class Grade(models.IntegerChoices):
        TWO = 2, "2-sinf"
        THREE = 3, "3-sinf"
        FOUR = 4, "4-sinf"
        FIVE = 5, "5-sinf"
        SIX = 6, "6-sinf"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    grade = models.PositiveSmallIntegerField(
        choices=Grade.choices,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
