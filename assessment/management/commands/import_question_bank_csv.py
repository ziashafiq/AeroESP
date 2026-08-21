import csv
from pathlib import Path

from django.contrib.auth import (
    get_user_model,
)
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from assessment.forms import (
    TeacherQuestionForm,
)
from assessment.models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


class Command(BaseCommand):

    help = (
        "Import validated AeroESP questions "
        "from a CSV file."
    )

    def add_arguments(
        self,
        parser,
    ):

        parser.add_argument(
            "csv_file",
        )

        parser.add_argument(
            "--owner",
            required=True,
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
        )

    def handle(
        self,
        *args,
        **options,
    ):

        path = Path(
            options["csv_file"]
        )

        if not path.exists():

            raise CommandError(
                f"CSV file not found: {path}"
            )

        User = get_user_model()

        try:

            owner = User.objects.get(
                username=options["owner"]
            )

        except User.DoesNotExist:

            raise CommandError(
                "Owner username does not exist."
            )

        profile = getattr(
            owner,
            "teacher_profile",
            None,
        )

        if (
            not owner.is_superuser
            and (
                profile is None
                or not profile.is_approved
            )
        ):

            raise CommandError(
                "Owner must be an approved "
                "teacher or superuser."
            )

        created = 0
        errors = 0
        skipped = 0

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:

            reader = csv.DictReader(
                handle
            )

            for row_number, row in enumerate(
                reader,
                start=2,
            ):

                track = (
                    row.get(
                        "track",
                        "",
                    )
                    .strip()
                )

                domain_ref = ""
                topic_ref = ""

                if (
                    track
                    == Question.Track.AEROSPACE_ESP
                ):

                    domain_code = (
                        row.get(
                            "domain_code",
                            "",
                        )
                        .strip()
                    )

                    topic_name = (
                        row.get(
                            "topic_name",
                            "",
                        )
                        .strip()
                    )

                    try:

                        domain = (
                            AerospaceDomain.objects
                            .get(
                                code=domain_code
                            )
                        )

                    except AerospaceDomain.DoesNotExist:

                        self.stderr.write(
                            f"Row {row_number}: "
                            f"unknown domain "
                            f"'{domain_code}'."
                        )

                        errors += 1
                        continue

                    domain_ref = str(
                        domain.pk
                    )

                    if topic_name:

                        try:

                            topic = (
                                AerospaceTopic.objects
                                .get(
                                    domain=domain,
                                    name=topic_name,
                                    is_active=True,
                                )
                            )

                        except AerospaceTopic.DoesNotExist:

                            self.stderr.write(
                                f"Row {row_number}: "
                                f"unknown topic "
                                f"'{topic_name}'."
                            )

                            errors += 1
                            continue

                        topic_ref = str(
                            topic.pk
                        )

                # Extract field values for duplicate check and form
                question_text = (
                    row.get(
                        "question_text",
                        "",
                    ).strip()
                )

                skill = (
                    row.get(
                        "skill",
                        "",
                    ).strip()
                )

                source_reference = (
                    row.get(
                        "source_reference",
                        "",
                    ).strip()
                )

                # Duplicate check
                duplicate_exists = (
                    Question.objects
                    .filter(
                        owner=owner,
                        track=track,
                        skill=skill,
                        question_text=question_text,
                        source_reference=source_reference,
                    )
                    .exists()
                )

                if duplicate_exists:
                    skipped += 1
                    continue

                form_data = {

                    "question_text": question_text,

                    "option_a": (
                        row.get(
                            "option_a",
                            "",
                        ).strip()
                    ),

                    "option_b": (
                        row.get(
                            "option_b",
                            "",
                        ).strip()
                    ),

                    "option_c": (
                        row.get(
                            "option_c",
                            "",
                        ).strip()
                    ),

                    "option_d": (
                        row.get(
                            "option_d",
                            "",
                        ).strip()
                    ),

                    "correct_answer": (
                        row.get(
                            "correct_answer",
                            "",
                        )
                        .strip()
                        .upper()
                    ),

                    "explanation": (
                        row.get(
                            "explanation",
                            "",
                        ).strip()
                    ),

                    "question_language": (
                        Question.Language.ENGLISH
                    ),

                    "options_language": (
                        Question.Language.ENGLISH
                    ),

                    "track": track,

                    "skill": skill,

                    "domain_ref": (
                        domain_ref
                    ),

                    "topic_ref": (
                        topic_ref
                    ),

                    "difficulty": (
                        row.get(
                            "difficulty",
                            "",
                        ).strip()
                    ),

                    "source_reference": source_reference,

                    "visibility": (
                        Question.Visibility.PRIVATE
                    ),
                }

                form = TeacherQuestionForm(
                    data=form_data
                )

                if not form.is_valid():

                    errors += 1

                    self.stderr.write(
                        f"Row {row_number}: "
                        f"{form.errors.as_text()}"
                    )

                    continue

                if options["dry_run"]:

                    created += 1
                    continue

                question = form.save(
                    commit=False
                )

                question.owner = owner

                question.source_type = (
                    Question.SourceType.IMPORTED
                )

                question.status = (
                    Question.Status.DRAFT
                )

                question.save()

                created += 1

        mode = (
            "validated"
            if options["dry_run"]
            else "imported"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{created} question(s) "
                f"{mode}; "
                f"{skipped} skipped; "
                f"{errors} error(s)."
            )
        )

        if errors:

            raise CommandError(
                "Question import completed "
                "with validation errors."
            )