
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Course(models.Model):
    """Junior Deutsch va Deutsch Plus kabi o'quv kurslari."""

    class Group(models.TextChoices):
        JUNIOR = "junior", "Junior Deutsch"
        PLUS = "plus", "Deutsch Plus"

    title = models.CharField(
        max_length=150,
        verbose_name="Kurs nomi"
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
        verbose_name="URL nomi"
    )

    group = models.CharField(
        max_length=20,
        choices=Group.choices,
        verbose_name="Kurs guruhi"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Kurs haqida"
    )

    cover = models.ImageField(
        upload_to="courses/covers/",
        blank=True,
        null=True,
        verbose_name="Kurs rasmi"
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name="Nashr qilingan"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        ordering = ["title"]

    def __str__(self):
        return self.title


class CourseGrade(models.Model):
    """Kursga biriktirilgan sinflar."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Kurs"
    )

    grade = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2),
            MaxValueValidator(6)
        ],
        choices=[
            (2, "2-sinf"),
            (3, "3-sinf"),
            (4, "4-sinf"),
            (5, "5-sinf"),
            (6, "6-sinf"),
        ],
        verbose_name="Sinf"
    )

    class Meta:
        verbose_name = "Kurs sinfi"
        verbose_name_plural = "Kurs sinflari"
        ordering = ["grade"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "grade"],
                name="unique_course_grade"
            )
        ]

    def __str__(self):
        return f"{self.course.title} — {self.grade}-sinf"


class Topic(models.Model):
    """Kurs ichidagi mavzular."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="Kurs"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Mavzu nomi"
    )

    slug = models.SlugField(
        max_length=220,
        verbose_name="URL nomi"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Mavzu tavsifi"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Tartib raqami"
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name="Nashr qilingan"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Mavzu"
        verbose_name_plural = "Mavzular"
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "slug"],
                name="unique_topic_slug_per_course"
            )
        ]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    """Mavzu tarkibidagi alohida dars."""

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Mavzu"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Dars nomi"
    )

    slug = models.SlugField(
        max_length=220,
        verbose_name="URL nomi"
    )

    summary = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Qisqa mazmun"
    )

    content = models.TextField(
        blank=True,
        verbose_name="Dars matni"
    )

    learning_objectives = models.TextField(
        blank=True,
        verbose_name="Dars maqsadlari"
    )

    duration_minutes = models.PositiveSmallIntegerField(
        default=15,
        validators=[MinValueValidator(1)],
        verbose_name="Davomiyligi (daqiqa)"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Tartib raqami"
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name="Nashr qilingan"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Dars"
        verbose_name_plural = "Darslar"
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["topic", "slug"],
                name="unique_lesson_slug_per_topic"
            )
        ]

    def __str__(self):
        return self.title


class LessonMaterial(models.Model):
    """Darsga biriktiriladigan fayllar."""

    class MaterialType(models.TextChoices):
        IMAGE = "image", "Rasm"
        AUDIO = "audio", "Audio"
        PDF = "pdf", "PDF hujjat"
        DOCUMENT = "document", "Hujjat"
        OTHER = "other", "Boshqa"

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="materials",
        verbose_name="Dars"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Material nomi"
    )

    material_type = models.CharField(
        max_length=20,
        choices=MaterialType.choices,
        default=MaterialType.OTHER,
        verbose_name="Material turi"
    )

    file = models.FileField(
        upload_to="courses/materials/%Y/%m/",
        verbose_name="Fayl"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Tartib raqami"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Dars materiali"
        verbose_name_plural = "Dars materiallari"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.lesson.title} — {self.title}"
