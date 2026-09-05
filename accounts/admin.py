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

    list_display_links = (
        "user",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    )

    list_filter = (
        "approval_status",
        "university",
        "department",
    )

    autocomplete_fields = (
        "user",
        "approved_by",
    )

    fieldsets = (
        (
            "Teacher information",
            {
                "fields": (
                    "user",
                    "university",
                    "department",
                    "academic_email",
                )
            }
        ),
        (
            "Approval",
            {
                "fields": (
                    "approval_status",
                    "approved_at",
                    "approved_by",
                )
            }
        ),
    )