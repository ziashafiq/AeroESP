"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()


# Same guard as config/wsgi.py: settings tolerate missing database
# credentials so a build can run, but a server must not start without
# them. See the comment there.

from django.conf import settings  # noqa: E402

if settings.DB_MISSING_CREDENTIALS:

    raise RuntimeError(
        "Refusing to start: the following database environment "
        "variables are unset - "
        + ", ".join(settings.DB_MISSING_CREDENTIALS)
        + ". Set them in your hosting panel (Liara: App -> "
        "Environment Variables) and redeploy."
    )
