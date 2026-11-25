
from django.contrib import admin
from .models import (
    Course,
    CourseGrade,
    Topic,
    Lesson,
    LessonMaterial,
)


class CourseGradeInline(admin.TabularInline):
    model = CourseGrade
    extra = 1


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = (
        "title",
        "slug",
        "order",
        "duration_minutes",
        "is_published",
    )


class LessonMaterialInline(admin.TabularInline):
    model = LessonMaterial
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "group",
        "is_published",
        "created_at",
    )

    list_filter = (
        "group",
        "is_published",
    )

    search_fields = (
        "title",
        "description",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    inlines = [CourseGradeInline]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "course",
        "order",
        "is_published",
    )

    list_filter = (
        "course",
        "is_published",
    )

    search_fields = (
        "title",
        "description",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "topic",
        "duration_minutes",
        "order",
        "is_published",
    )

    list_filter = (
        "topic__course",
        "is_published",
    )

    search_fields = (
        "title",
        "summary",
        "content",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    inlines = [LessonMaterialInline]


@admin.register(LessonMaterial)
class LessonMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "lesson",
        "material_type",
        "order",
    )

    list_filter = (
        "material_type",
    )

    search_fields = (
        "title",
        "lesson__title",
    )
