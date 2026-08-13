from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import CustomUser, StudentProfile, TeacherProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "student_id",
        "university",
        "primary_aerospace_field",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "student_id",
        "university",
    )

    list_filter = (
        "primary_aerospace_field",
        "university",
    )


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "university",
        "department",
        "approval_status",
        "approved_by",
        "approved_at",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "academic_email",
        "university",
    )

    list_filter = (
        "approval_status",
        "university",
        "department",
    )

    actions = (
        "approve_teachers",
        "reject_teachers",
    )

    @admin.action(description="Approve selected teachers")
    def approve_teachers(self, request, queryset):
        queryset.update(
            approval_status=TeacherProfile.ApprovalStatus.APPROVED,
            approved_by=request.user,
            approved_at=timezone.now(),
        )

    @admin.action(description="Reject selected teachers")
    def reject_teachers(self, request, queryset):
        queryset.update(
            approval_status=TeacherProfile.ApprovalStatus.REJECTED,
            approved_by=request.user,
            approved_at=timezone.now(),
        )