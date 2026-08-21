from django.contrib import admin

from .models import (
    CourseModule,
    Enrollment,
    GuideResource,
    LearnerError,
    LearningCourse,
    LearningItem,
    LearningItemQuestion,
    LearningProgram,
    LearningProgress,
    Resource,
)


@admin.register(LearningProgram)
class LearningProgramAdmin(
    admin.ModelAdmin
):
    list_display = (
        "title",
        "program_type",
        "is_active",
        "order",
    )

    list_filter = (
        "program_type",
        "is_active",
    )

    search_fields = (
        "title",
        "title_fa",
        "code",
    )


@admin.register(LearningCourse)
class LearningCourseAdmin(
    admin.ModelAdmin
):
    list_display = (
        "title",
        "program",
        "level",
        "is_active",
        "is_public",
    )

    list_filter = (
        "program",
        "level",
        "is_active",
        "is_public",
    )

    search_fields = (
        "title",
        "title_fa",
        "code",
    )


@admin.register(CourseModule)
class CourseModuleAdmin(
    admin.ModelAdmin
):
    list_display = (
        "title",
        "course",
        "module_type",
        "order",
        "is_active",
    )

    list_filter = (
        "module_type",
        "is_active",
        "course",
    )


@admin.register(LearningItem)
class LearningItemAdmin(
    admin.ModelAdmin
):
    list_display = (
        "title",
        "module",
        "item_type",
        "created_by",
        "is_verified",
        "is_public",
    )

    list_filter = (
        "item_type",
        "source_type",
        "is_verified",
        "is_public",
    )

    search_fields = (
        "title",
        "definition_en",
        "meaning_fa",
        "example",
        "common_mistake",
        "correct_form",
    )


@admin.register(
    LearningItemQuestion
)
class LearningItemQuestionAdmin(
    admin.ModelAdmin
):
    list_display = (
        "learning_item",
        "question",
        "created_at",
    )


@admin.register(Enrollment)
class EnrollmentAdmin(
    admin.ModelAdmin
):
    list_display = (
        "student",
        "course",
        "status",
        "enrolled_at",
    )

    list_filter = (
        "status",
        "course",
    )


@admin.register(LearningProgress)
class LearningProgressAdmin(
    admin.ModelAdmin
):
    list_display = (
        "student",
        "learning_item",
        "status",
        "mastery_score",
        "next_review_at",
    )

    list_filter = (
        "status",
    )


@admin.register(LearnerError)
class LearnerErrorAdmin(
    admin.ModelAdmin
):
    list_display = (
        "student",
        "category",
        "is_general_english_error",
        "is_esp_specific_error",
        "resolved",
        "occurred_at",
    )

    list_filter = (
        "category",
        "is_general_english_error",
        "is_esp_specific_error",
        "resolved",
    )

    search_fields = (
        "student__username",
        "student_response",
        "expected_response",
        "note",
    )


@admin.register(Resource)
class ResourceAdmin(
    admin.ModelAdmin
):
    list_display = (
        "title",
        "resource_type",
        "visibility",
        "course",
        "module",
        "uploaded_by",
        "is_active",
        "created_at",
    )

    list_filter = (
        "resource_type",
        "visibility",
        "is_active",
        "course",
        "module",
    )

    search_fields = (
        "title",
        "description",
        "uploaded_by__username",
    )


@admin.register(GuideResource)
class GuideResourceAdmin(
    admin.ModelAdmin
):
    list_display = (
        "title",
        "category",
        "recommended_level",
        "is_public",
    )

    list_filter = (
        "category",
        "is_public",
    )

    search_fields = (
        "title",
        "description",
    )