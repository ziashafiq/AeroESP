from django.core.management.base import BaseCommand
from django.db import transaction

from assessment.models import Question
from learning.models import (
    LearningItem,
    LearningItemQuestion,
)


class Command(BaseCommand):

    help = (
        "Safely link eligible question-bank questions "
        "to compatible learning items."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--apply",
            action="store_true",
            help=(
                "Create links. Without this option, "
                "the command runs in dry-run mode."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):

        apply_changes = options["apply"]

        questions = (
            Question.objects
            .filter(
                track="AEROSPACE_ESP",
                status__in=[
                    "APPROVED",
                    "DEMO",
                ],
            )
            .exclude(
                visibility="EXAM_ONLY",
            )
            .select_related(
                "domain_ref",
                "topic_ref",
            )
            .order_by("pk")
        )

        learning_items = list(
            LearningItem.objects
            .filter(
                is_public=True,
            )
            .select_related(
                "aerospace_domain",
                "aerospace_topic",
            )
            .order_by("pk")
        )

        created_count = 0
        existing_count = 0

        topic_match_count = 0
        domain_match_count = 0

        skipped_no_match = 0
        skipped_ambiguous = 0

        examples = []

        for question in questions:

            candidates = []

            match_type = None

            # ---------------------------------------------
            # LEVEL 1:
            # Exact aerospace topic match
            # ---------------------------------------------

            if question.topic_ref_id:

                candidates = [
                    item
                    for item in learning_items
                    if (
                        item.aerospace_topic_id
                        == question.topic_ref_id
                    )
                ]

                if candidates:
                    match_type = "TOPIC"

            # ---------------------------------------------
            # LEVEL 2:
            # Aerospace domain fallback
            # ---------------------------------------------

            if (
                not candidates
                and question.domain_ref_id
            ):

                candidates = [
                    item
                    for item in learning_items
                    if (
                        item.aerospace_domain_id
                        == question.domain_ref_id
                    )
                ]

                if candidates:
                    match_type = "DOMAIN"

            # ---------------------------------------------
            # No compatible LearningItem
            # ---------------------------------------------

            if not candidates:

                skipped_no_match += 1
                continue

            # ---------------------------------------------
            # Avoid arbitrary selection
            # ---------------------------------------------

            if len(candidates) != 1:

                skipped_ambiguous += 1

                if len(examples) < 10:

                    examples.append(
                        (
                            question.pk,
                            "AMBIGUOUS",
                            [
                                item.pk
                                for item
                                in candidates
                            ],
                        )
                    )

                continue

            learning_item = candidates[0]

            if match_type == "TOPIC":
                topic_match_count += 1

            elif match_type == "DOMAIN":
                domain_match_count += 1

            exists = (
                LearningItemQuestion.objects
                .filter(
                    learning_item=learning_item,
                    question=question,
                )
                .exists()
            )

            if exists:

                existing_count += 1
                continue

            if apply_changes:

                LearningItemQuestion.objects.create(
                    learning_item=learning_item,
                    question=question,
                )

                created_count += 1

            else:

                created_count += 1

            if len(examples) < 10:

                examples.append(
                    (
                        question.pk,
                        match_type,
                        learning_item.pk,
                        learning_item.title,
                    )
                )

        # ---------------------------------------------
        # Dry-run rollback safeguard
        # ---------------------------------------------

        if not apply_changes:

            transaction.set_rollback(True)

        mode = (
            "APPLY"
            if apply_changes
            else "DRY RUN"
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                f"Mode: {mode}"
            )
        )

        self.stdout.write(
            f"Eligible questions: {questions.count()}"
        )

        self.stdout.write(
            f"Public learning items: "
            f"{len(learning_items)}"
        )

        self.stdout.write(
            f"Topic matches: {topic_match_count}"
        )

        self.stdout.write(
            f"Domain matches: {domain_match_count}"
        )

        self.stdout.write(
            f"New link candidates: {created_count}"
        )

        self.stdout.write(
            f"Existing links: {existing_count}"
        )

        self.stdout.write(
            f"Skipped - no safe match: "
            f"{skipped_no_match}"
        )

        self.stdout.write(
            f"Skipped - ambiguous: "
            f"{skipped_ambiguous}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Sample decisions:"
        )

        for example in examples:
            self.stdout.write(
                f"  {example}"
            )

        if apply_changes:

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Question-bank linking completed."
                )
            )

        else:

            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Dry run only. "
                    "No database changes were saved."
                )
            )