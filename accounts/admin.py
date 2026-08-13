from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import (
    CustomUser,
    StudentProfile,
    TeacherProfile,
)


# =========================================================
# AeroESP Admin Branding / Navigation
# =========================================================

admin.site.site_header = "AeroESP Administration"
admin.site.site_title = "AeroESP Admin"
admin.site.index_title = "AeroESP Administration"

# The "View site" button in Django Admin will now open
# the universal AeroESP Account Center.
admin.site.site_url = "/accounts/account/"


# =========================================================
# Users
# =========================================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )

    ordering = (
        "username",
    )


# =========================================================
# Students
# =========================================================

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
        "user__email",
        "student_id",
        "university",
    )

    search_help_text = (
        "Search by username, student ID, "
        "name, email, or university."
    )

    list_filter = (
        "primary_aerospace_field",
        "university",
    )

    list_per_page = 50


# =========================================================
# Teachers
# =========================================================

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
        "user__email",
        "academic_email",
        "university",
        "department",
    )

    search_help_text = (
        "Search by teacher name, username, "
        "email, department, or university."
    )

    list_filter = (
        "approval_status",
        "university",
        "department",
    )

    list_per_page = 50

    actions = (
        "approve_teachers",
        "reject_teachers",
    )

    @admin.action(
        description="Approve selected teachers"
    )
    def approve_teachers(
        self,
        request,
        queryset,
    ):

        queryset.update(
            approval_status=(
                TeacherProfile
                .ApprovalStatus
                .APPROVED
            ),
            approved_by=request.user,
            approved_at=timezone.now(),
        )

    @admin.action(
        description="Reject selected teachers"
    )
    def reject_teachers(
        self,
        request,
        queryset,
    ):

        queryset.update(
            approval_status=(
                TeacherProfile
                .ApprovalStatus
                .REJECTED
            ),
            approved_by=request.user,
            approved_at=timezone.now(),
        )