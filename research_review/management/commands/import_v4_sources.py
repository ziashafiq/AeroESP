import hashlib
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from research_review.models import ResearchExperiment


SOURCE_FILES = {
    "R003": Path(
        r"D:\AeroESP_backup_pre_customuser\make_q_by_ai"
        r"\_AEROESP_GEN4_Q_extracted.txt"
    ),
    "R004": Path(
        r"D:\AeroESP_backup_pre_customuser\make_q_by_ai"
        r"\_r004_extracted.txt"
    ),
    "R005": Path(
        r"D:\AeroESP_backup_pre_customuser\make_q_by_ai"
        r"\_r005_extracted.txt"
    ),
    "R006": Path(
        r"D:\AeroESP_backup_pre_customuser\make_q_by_ai"
        r"\_r006_extracted.txt"
    ),
    "R007": Path(
        r"D:\AeroESP_backup_pre_customuser\make_q_by_ai"
        r"\_r007_extracted.txt"
    ),
}


START_MARKER = "SOURCE MATERIAL:"
END_MARKER = "Generate the required JSON assessment now."


def extract_source_material(path):
    if not path.exists():
        raise CommandError(
            f"Source file not found: {path}"
        )

    text = path.read_text(
        encoding="utf-8"
    )

    if START_MARKER not in text:
        raise CommandError(
            f"SOURCE MATERIAL marker not found: {path}"
        )

    source = text.split(
        START_MARKER,
        1,
    )[1]

    if END_MARKER not in source:
        raise CommandError(
            f"End marker not found: {path}"
        )

    source = source.split(
        END_MARKER,
        1,
    )[0]

    source = source.strip()

    if len(source) < 500:
        raise CommandError(
            f"Extracted source appears too short: {path}"
        )

    return source


class Command(BaseCommand):

    help = (
        "Import the exact frozen V4 source materials "
        "for R003-R007."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write source materials to the database.",
        )

    def handle(self, *args, **options):

        apply_changes = options["apply"]

        extracted = {}

        self.stdout.write(
            "\nV4 SOURCE MATERIAL AUDIT\n"
        )

        for source_id, path in SOURCE_FILES.items():

            source = extract_source_material(
                path
            )

            digest = hashlib.sha256(
                source.encode("utf-8")
            ).hexdigest()

            extracted[source_id] = source

            self.stdout.write(
                f"{source_id}: "
                f"{len(source)} chars | "
                f"SHA256={digest}"
            )

        expected_ids = set(
            SOURCE_FILES.keys()
        )

        database_ids = set(
            ResearchExperiment.objects
            .filter(
                source_id__in=expected_ids
            )
            .values_list(
                "source_id",
                flat=True,
            )
        )

        if database_ids != expected_ids:
            raise CommandError(
                "Database experiment set does not match "
                "R003-R007."
            )

        self.stdout.write(
            "\nSOURCE EXTRACTION PASSED."
        )

        if not apply_changes:

            self.stdout.write(
                "\nDRY RUN ONLY - database was NOT modified."
            )

            self.stdout.write(
                "Run again with --apply after reviewing."
            )

            return

        with transaction.atomic():

            for source_id, source in extracted.items():

                experiment = (
                    ResearchExperiment.objects
                    .select_for_update()
                    .get(
                        source_id=source_id
                    )
                )

                experiment.source_material = source

                experiment.save(
                    update_fields=[
                        "source_material",
                    ]
                )

        self.stdout.write(
            "\nSOURCE MATERIAL IMPORT COMPLETE."
        )

        for experiment in (
            ResearchExperiment.objects
            .filter(
                source_id__in=expected_ids
            )
            .order_by("source_id")
        ):

            self.stdout.write(
                f"{experiment.source_id}: "
                f"{len(experiment.source_material)} chars"
            )