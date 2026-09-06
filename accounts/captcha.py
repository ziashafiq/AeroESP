"""
A self-contained image captcha.

Depends only on Pillow, which the project already installs for
ImageField support. Nothing is fetched from another host at any point:
the challenge is drawn here, stored here, and checked here. That is the
requirement this replaces django-simple-captcha for - the package is
absent from some package mirrors, and the hosted alternatives
(reCAPTCHA, hCaptcha) load scripts from domains that are not reliably
reachable everywhere this is used.

The answer itself is never stored. The rendered PNG is kept with the
row so the image view can serve it without needing to redraw, and only
a keyed hash of the answer is retained for checking.
"""

import hashlib
import hmac
import io
import math
import random
import secrets

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from PIL import Image, ImageDraw, ImageFilter, ImageFont


# 0/O and 1/I/L are guesswork at this size, so they are left out.
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

DEFAULT_LENGTH = 5

DEFAULT_TTL_MINUTES = 10

IMAGE_SIZE = (170, 60)

FONT_SIZE = 36

BACKGROUND = (255, 255, 255)

INK = (11, 27, 58)

# Accepted in tests instead of solving an image.
TEST_RESPONSE = "PASSED"


def _setting(name, default):
    return getattr(settings, name, default)


def normalise(response):
    """
    Fold away the differences a human should not be punished for.
    """

    return "".join((response or "").split()).upper()


def hash_answer(answer):
    """
    Keyed digest, so that read access to the table does not hand over
    the pending answers.
    """

    return hmac.new(
        settings.SECRET_KEY.encode(),
        normalise(answer).encode(),
        hashlib.sha256,
    ).hexdigest()


def random_answer(length=None):

    length = length or _setting(
        "AEROESP_CAPTCHA_LENGTH",
        DEFAULT_LENGTH,
    )

    return "".join(
        secrets.choice(ALPHABET)
        for _ in range(length)
    )


def render_image(text):
    """
    Draw the challenge: rotated glyphs on a noisy background.

    The distortions are deliberately mild. A captcha that defeats every
    bot but half the humans has failed at its actual job, and this only
    needs to stop bulk automated sign-ups.
    """

    width, height = IMAGE_SIZE

    image = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default(size=FONT_SIZE)

    # Faint background clutter, drawn first so glyphs stay on top.
    for _ in range(random.randint(4, 7)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        draw.arc(
            [x1 - 40, y1 - 40, x1 + 40, y1 + 40],
            start=random.randint(0, 360),
            end=random.randint(0, 360),
            fill=(190, 200, 215),
            width=2,
        )

    for _ in range(220):
        draw.point(
            (
                random.randint(0, width),
                random.randint(0, height),
            ),
            fill=(205, 212, 225),
        )

    # Each glyph is drawn on its own transparent tile, rotated, then
    # pasted. Rotating the whole word would leave it machine-readable.
    step = (width - 20) // max(len(text), 1)
    x = 12

    for character in text:

        tile = Image.new("RGBA", (step + 18, height), (0, 0, 0, 0))
        tile_draw = ImageDraw.Draw(tile)

        tile_draw.text(
            (4, 6),
            character,
            font=font,
            fill=INK + (255,),
        )

        tile = tile.rotate(
            random.uniform(-26, 26),
            resample=Image.BICUBIC,
            expand=False,
        )

        image.paste(
            tile,
            (x, random.randint(-6, 4)),
            tile,
        )

        x += step

    # A single sine warp across the whole image.
    warped = image.copy()
    pixels = warped.load()
    source = image.load()
    amplitude = 2.5
    period = random.uniform(45, 75)

    for y in range(height):
        offset = int(
            amplitude * math.sin(2 * math.pi * y / period)
        )
        for column in range(width):
            source_x = min(
                max(column + offset, 0),
                width - 1,
            )
            pixels[column, y] = source[source_x, y]

    warped = warped.filter(ImageFilter.SMOOTH)

    buffer = io.BytesIO()
    warped.save(buffer, format="PNG", optimize=True)

    return buffer.getvalue()


def create_challenge():
    """
    Issue a challenge and return the stored row.
    """

    from .models import CaptchaChallenge

    # Opportunistic cleanup: expired rows have no further use, and this
    # keeps the table from growing without a scheduled job.
    CaptchaChallenge.objects.filter(
        expires_at__lte=timezone.now(),
    ).delete()

    answer = random_answer()

    ttl = _setting(
        "AEROESP_CAPTCHA_TTL_MINUTES",
        DEFAULT_TTL_MINUTES,
    )

    return CaptchaChallenge.objects.create(
        key=secrets.token_hex(20),
        answer_hash=hash_answer(answer),
        image=render_image(answer),
        expires_at=(
            timezone.now() + timedelta(minutes=ttl)
        ),
    )


def verify(key, response):
    """
    Check an answer and consume the challenge.

    A challenge is valid for exactly one attempt, so a wrong answer
    costs the sender a fresh image rather than allowing a guessing
    loop against the same one.
    """

    from .models import CaptchaChallenge

    if not key or not response:
        return False

    challenge = CaptchaChallenge.objects.filter(
        key=key,
        expires_at__gt=timezone.now(),
    ).first()

    if challenge is None:
        return False

    expected = challenge.answer_hash

    challenge.delete()

    return hmac.compare_digest(
        expected,
        hash_answer(response),
    )
