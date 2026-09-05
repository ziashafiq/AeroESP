"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()


# Settings deliberately tolerate absent database credentials so that
# build steps (collectstatic) can run before the host injects its
# runtime environment. This module is imported only by the web server,
# which means the credentials must be there by now: fail here, with a
# message naming the variables, rather than serving a site that answers
# every request with an authentication error.

from django.conf import settings  # noqa: E402

if settings.DB_MISSING_CREDENTIALS:

    raise RuntimeError(
        "Refusing to start: the following database environment "
        "variables are unset - "
        + ", ".join(settings.DB_MISSING_CREDENTIALS)
        + ". Set them in your hosting panel (Liara: App -> "
        "Environment Variables) and redeploy."
    )
