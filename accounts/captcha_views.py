from django.http import (
    Http404,
    HttpResponse,
    JsonResponse,
)
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .captcha import create_challenge
from .models import CaptchaChallenge


@require_GET
def captcha_image(request, key):
    """
    Serve the PNG that was rendered when the challenge was issued.
    """

    challenge = CaptchaChallenge.objects.filter(
        key=key,
        expires_at__gt=timezone.now(),
    ).first()

    if challenge is None:
        raise Http404("This captcha has expired.")

    wants_dark = (
        request.GET.get("theme", "").lower() == "dark"
    )

    data = (
        challenge.image_dark
        if wants_dark and challenge.image_dark
        else challenge.image
    )

    response = HttpResponse(
        bytes(data),
        content_type="image/png",
    )

    # Every challenge is single use, so a cached copy would only ever
    # show an image whose answer is no longer accepted.
    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )

    return response


@require_GET
def captcha_refresh(request):
    """
    Issue a replacement challenge for the "New image" button.
    """

    challenge = create_challenge()

    return JsonResponse(
        {
            "key": challenge.key,
            "image_url": reverse(
                "captcha_image",
                args=[challenge.key],
            ),
        }
    )
