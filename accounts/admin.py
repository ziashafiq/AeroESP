from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from unfold.admin import ModelAdmin
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)

from .models import (
    CustomUser,
    HelpGuide,
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


# Starting point for a hand-promoted reviewer's profile. It is only a
# default: discipline and institution stay editable on the
# ExpertReviewerProfile page afterwards.
REVIEWER_DEFAULT_DISCIPLINE = "AEROSPACE"


# =========================================================
# Users
# =========================================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, ModelAdmin):

    # UserAdmin first so its fieldsets/add_fieldsets and password
    # handling still win; ModelAdmin second purely for Unfold's
    # rendering. The three form overrides are Unfold's restyled
    # versions of the stock auth forms - same validation, same
    # password hashing, only the widgets differ. Without them the
    # password field renders as unstyled markup inside the new theme.
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

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
class StudentProfileAdmin(ModelAdmin):

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
class TeacherProfileAdmin(ModelAdmin):

    list_display = (
        "user",
        "university",
        "department",
        "approval_status",
        # Shown next to approval_status precisely because the two are
        # now independent: the column makes it obvious that approving
        # someone did not also make them a reviewer.
        "is_expert_reviewer",
        "approved_by",
        "approved_at",
    )

    list_display_links = (
        "user",
    )

    list_select_related = (
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

    # Reviewer status is a separate decision from teacher approval, so
    # it is a separate deliberate gesture. Approving a teacher used to
    # create an active ExpertReviewerProfile as a side effect; see
    # revoke_reviewer_access_on_rejection in accounts/signals.py.
    actions = (
        "promote_to_expert_reviewer",
        "revoke_expert_reviewer",
    )

    @admin.display(
        description="Expert reviewer",
        boolean=True,
    )
    def is_expert_reviewer(self, obj):
        profile = getattr(
            obj.user,
            "expert_reviewer_profile",
            None,
        )
        return bool(profile and profile.is_active_reviewer)

    @admin.action(
        description="Promote to expert reviewer",
    )
    def promote_to_expert_reviewer(self, request, queryset):
        """
        Create (or re-activate) an ExpertReviewerProfile for each
        selected teacher.

        Imported lazily for the same reason the signal does it:
        accounts must not depend on research_review at import time.
        """

        from research_review.models import ExpertReviewerProfile

        created = 0
        reactivated = 0
        already = 0
        skipped = []

        for profile in queryset.select_related("user"):

            # Reviewing implies the teacher account itself is in good
            # standing. Refusing here keeps the two decisions
            # independent without letting the second contradict the
            # first.
            if (
                profile.approval_status
                != TeacherProfile.ApprovalStatus.APPROVED
            ):
                skipped.append(profile.user.username)
                continue

            reviewer, was_created = (
                ExpertReviewerProfile.objects.get_or_create(
                    user=profile.user,
                    defaults={
                        "discipline": REVIEWER_DEFAULT_DISCIPLINE,
                        "institution": profile.university,
                        "is_active_reviewer": True,
                    },
                )
            )

            if was_created:
                created += 1
                continue

            if not reviewer.is_active_reviewer:
                reviewer.is_active_reviewer = True
                reviewer.save(update_fields=["is_active_reviewer"])
                reactivated += 1
            else:
                already += 1

        if created or reactivated:
            self.message_user(
                request,
                f"Expert reviewer access granted: {created} created, "
                f"{reactivated} re-activated.",
                messages.SUCCESS,
            )

        if already:
            self.message_user(
                request,
                f"{already} already had active reviewer access.",
                messages.INFO,
            )

        if skipped:
            self.message_user(
                request,
                "Not promoted - the teacher account is not approved: "
                + ", ".join(skipped),
                messages.WARNING,
            )

    @admin.action(
        description="Revoke expert reviewer access",
    )
    def revoke_expert_reviewer(self, request, queryset):
        """
        Deactivate reviewer access without deleting the profile, so
        the reviewer_code and any completed reviews stay intact.
        """

        from research_review.models import ExpertReviewerProfile

        updated = ExpertReviewerProfile.objects.filter(
            user__in=queryset.values("user"),
            is_active_reviewer=True,
        ).update(
            is_active_reviewer=False,
        )

        self.message_user(
            request,
            f"Expert reviewer access revoked for {updated} "
            f"reviewer(s). Their profiles and past reviews are kept.",
            messages.SUCCESS if updated else messages.INFO,
        )


# =========================================================
# Help Guides
# =========================================================

@admin.register(HelpGuide)
class HelpGuideAdmin(ModelAdmin):

    list_display = (
        "title",
        "audience",
        "is_published",
        "order",
        "updated_at",
    )

    list_display_links = (
        "title",
    )

    list_filter = (
        "audience",
        "is_published",
    )

    list_editable = (
        "is_published",
        "order",
    )

    search_fields = (
        "title",
        "summary",
        "body",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "audience",
                    "title",
                    "slug",
                    "summary",
                    "is_published",
                    "order",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "body",
                    "attachment",
                ),
                "description": (
                    "Fill in either the text, the file, or both. "
                    "Use slug 'expert-reviewer-getting-started' for "
                    "the guide that /expert-review/getting-started/ "
                    "opens automatically."
                ),
            },
        ),
    )
