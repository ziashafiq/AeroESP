from django.db import migrations


def copy_forward(apps, schema_editor):
    """
    "T1,D2,C1" -> ["T1", "D2", "C1"]. Empty/whitespace-only strings
    become [], matching error_codes_json's default so a review that
    never had any codes looks the same before and after.
    """

    ExpertReview = apps.get_model(
        "research_review",
        "ExpertReview",
    )

    for review in ExpertReview.objects.exclude(
        error_codes="",
    ).iterator():

        review.error_codes_json = [
            code.strip()
            for code in review.error_codes.split(",")
            if code.strip()
        ]

        review.save(
            update_fields=["error_codes_json"],
        )


def copy_backward(apps, schema_editor):
    """
    Reverse of copy_forward, for `migrate research_review 0006`.
    """

    ExpertReview = apps.get_model(
        "research_review",
        "ExpertReview",
    )

    for review in ExpertReview.objects.exclude(
        error_codes_json=[],
    ).iterator():

        review.error_codes = ",".join(
            review.error_codes_json
        )

        review.save(
            update_fields=["error_codes"],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('research_review', '0006_add_error_codes_json'),
    ]

    operations = [
        migrations.RunPython(
            copy_forward,
            copy_backward,
        ),
    ]
