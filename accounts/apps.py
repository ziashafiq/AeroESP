from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _sync_role_permissions(sender, **kwargs):
    """
    Grant the Teachers/Students groups their question-bank permissions
    the moment those permissions exist, on every migrate - not only
    when someone remembers to run `manage.py setup_roles` by hand.

    Group.objects.get_or_create() creates the "Teachers" group with no
    permissions attached the first time a TeacherProfile is saved
    (see accounts/signals.py); permission assignment only ever
    happened inside setup_roles. On a fresh deploy where that command
    is never run, an approved teacher gets 403 on the question bank -
    reproduced locally: a brand-new database, one approved
    TeacherProfile, GET /teacher/questions/ -> 403, with the Teachers
    group present but empty.

    Gated on the assessment app specifically, because Question's own
    permissions (assessment.view_question and friends) are what is
    being assigned, and django.contrib.auth's post_migrate handler -
    connected earlier, since django.contrib.auth precedes accounts in
    INSTALLED_APPS - has already created them for that dispatch by the
    time this receiver (connected in AccountsConfig.ready(), for every
    app's post_migrate) runs.
    """

    app_config = kwargs.get("app_config")

    if app_config is None or app_config.label != "assessment":
        return

    import io

    from django.core.management import call_command

    # verbosity=0 does not silence setup_roles's own stdout.write() -
    # it prints "AeroESP roles ready..." on every migrate otherwise.
    call_command(
        "setup_roles",
        verbosity=0,
        stdout=io.StringIO(),
    )


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        import accounts.signals  # noqa: F401

        post_migrate.connect(
            _sync_role_permissions,
            dispatch_uid="accounts_sync_role_permissions",
        )
