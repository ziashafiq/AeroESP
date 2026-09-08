from django.apps import AppConfig


class ResearchReviewConfig(AppConfig):
    name = 'research_review'

    # Without this the admin renders the app label verbatim, so the
    # heading above the research models read "Research_Review".
    verbose_name = "Research Review"
