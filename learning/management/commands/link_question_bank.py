from django.core.management.base import BaseCommand
from django.db import transaction

from assessment.models import Question
from learning.models import (
    LearningItem,
    LearningItemQuestion,
)


class Command(BaseCommand):

    help = (
        "Safely link eligible aerospace questions "
        "to learning items using exact taxonomy topic matches."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--apply",
            action="store_true",
            help=(
                "Create links. Without this option "
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
                topic_ref__isnull=False,
                domain_ref__isnull=False,
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
                aerospace_topic__isnull=False,
                aerospace_domain__isnull=False,
            )
            .select_related(
                "aerospace_domain",
                "aerospace_topic",
            )
            .order_by("pk")
        )

        candidate_count = 0
        created_count = 0
        existing_count = 0
        no_match_count = 0
        ambiguous_count = 0
        domain_mismatch_count = 0

        samples = []

        for question in questions:

            candidates = [
                item
                for item in learning_items
                if (
                    item.aerospace_topic_id
                    == question.topic_ref_id
                )
            ]

            if not candidates:

                no_match_count += 1
                continue

            if len(candidates) != 1:

                ambiguous_count += 1

                if len(samples) < 15:
                    samples.append(
                        (
                            question.pk,
                            "AMBIGUOUS",
                            [
                                item.pk
                                for item in candidates
                            ],
                        )
                    )

                continue

            learning_item = candidates[0]

            # Extra safety:
            # exact topic should also belong to
            # the same aerospace domain.
            if (
                learning_item.aerospace_domain_id
                != question.domain_ref_id
            ):

                domain_mismatch_count += 1

                if len(samples) < 15:
                    samples.append(
                        (
                            question.pk,
                            "DOMAIN_MISMATCH",
                            question.domain_ref_id,
                            learning_item.aerospace_domain_id,
                        )
                    )

                continue

            candidate_count += 1

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

            if len(samples) < 15:

                samples.append(
                    (
                        question.pk,
                        "EXACT_TOPIC",
                        learning_item.pk,
                        learning_item.title,
                    )
                )

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
            f"Eligible topic-tagged questions: "
            f"{questions.count()}"
        )

        self.stdout.write(
            f"Taxonomy learning items: "
            f"{len(learning_items)}"
        )

        self.stdout.write(
            f"Exact topic candidates: "
            f"{candidate_count}"
        )

        self.stdout.write(
            f"New links: "
            f"{created_count}"
        )

        self.stdout.write(
            f"Existing links: "
            f"{existing_count}"
        )

        self.stdout.write(
            f"No topic match: "
            f"{no_match_count}"
        )

        self.stdout.write(
            f"Ambiguous matches: "
            f"{ambiguous_count}"
        )

        self.stdout.write(
            f"Domain mismatches: "
            f"{domain_mismatch_count}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Sample decisions:"
        )

        for sample in samples:
            self.stdout.write(
                f"  {sample}"
            )

        if apply_changes:

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Exact taxonomy linking completed."
                )
            )

        else:

            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Dry run only. "
                    "No links were saved."
                )
            )