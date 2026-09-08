from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Let people sign in with their email address as well as the username
    AeroESP generated for them.

    Usernames here are derived from the email's local part, so they are
    exactly the thing a returning user does not remember. The email is
    the credential they do know.

    Two properties this must not break:

    1. No user enumeration. The failure path is identical whether or
       not the address exists - same generic message from the form,
       same work done here. `ModelBackend.authenticate` runs the
       password hasher once against a dummy hash when it finds no user,
       so that a missing account does not answer measurably faster than
       a wrong password; a lookup that returned early would reintroduce
       exactly that timing signal. So when no user matches, this hands
       control to super() with the original input rather than bailing
       out, and the dummy-hash run still happens.

    2. django-axes still sees every attempt. Axes wraps authentication
       through AxesStandaloneBackend and its middleware, both of which
       key off the credentials in the request rather than off which
       backend resolved the user, so lockout counting is unaffected by
       resolving a username from an email first.
    """

    def authenticate(
        self,
        request,
        username=None,
        password=None,
        **kwargs,
    ):

        User = get_user_model()

        identifier = username

        if identifier is None:
            identifier = kwargs.get(User.USERNAME_FIELD)

        # Only treat it as an email when it could not be a username.
        # Usernames here never contain "@", so this cannot shadow a
        # real username, and a non-email string skips the extra query.
        if identifier and "@" in identifier:

            # iexact, because addresses are stored lowercased at
            # registration but may be typed in any case.
            match = (
                User.objects.filter(email__iexact=identifier.strip())
                .order_by("pk")
                .first()
            )

            if match is not None:
                identifier = getattr(match, User.USERNAME_FIELD)

        return super().authenticate(
            request,
            username=identifier,
            password=password,
            **kwargs,
        )
