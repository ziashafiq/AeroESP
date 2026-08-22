from django.core.management.base import BaseCommand

from assessment.models import Question
from learning.models import (
    LearningItem,
    LearningItemQuestion,
)


class Command(BaseCommand):

    help = (
        "Audit AeroESP adaptive-practice taxonomy coverage "
        "and LearningItemQuestion integrity."
    )

    def handle(self, *args, **options):

        errors = []

        aerospace_questions = (
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
        )

        topic_questions = (
            aerospace_questions
            .filter(
                topic_ref__isnull=False,
            )
        )

        untagged_questions = (
            aerospace_questions
            .filter(
                topic_ref__isnull=True,
            )
        )

        taxonomy_items = (
            LearningItem.objects
            .filter(
                is_public=True,
                aerospace_topic__isnull=False,
            )
        )

        links = (
            LearningItemQuestion.objects
            .filter(
                question__track="AEROSPACE_ESP",
            )
            .select_related(
                "learning_item",
                "question",
            )
        )

        taxonomy_links = links.filter(
            learning_item__aerospace_topic__isnull=False,
        )

        invalid_topic_links = 0
        invalid_domain_links = 0
        duplicate_pairs = 0

        seen_pairs = set()

        for link in taxonomy_links:

            item = link.learning_item
            question = link.question

            pair = (
                item.pk,
                question.pk,
            )

            if pair in seen_pairs:
                duplicate_pairs += 1

            seen_pairs.add(pair)

            if (
                question.topic_ref_id
                != item.aerospace_topic_id
            ):
                invalid_topic_links += 1

            if (
                question.domain_ref_id
                != item.aerospace_domain_id
            ):
                invalid_domain_links += 1

        linked_question_ids = set(
            taxonomy_links.values_list(
                "question_id",
                flat=True,
            )
        )

        topic_question_ids = set(
            topic_questions.values_list(
                "id",
                flat=True,
            )
        )

        missing_topic_links = (
            topic_question_ids
            - linked_question_ids
        )

        self.stdout.write("")
        self.stdout.write(
            "AeroESP Adaptive Practice Readiness"
        )

        self.stdout.write(
            "=" * 60
        )

        self.stdout.write(
            f"Eligible Aerospace questions: "
            f"{aerospace_questions.count()}"
        )

        self.stdout.write(
            f"Questions with topic_ref: "
            f"{topic_questions.count()}"
        )

        self.stdout.write(
            f"Questions without topic_ref: "
            f"{untagged_questions.count()}"
        )

        self.stdout.write(
            f"Public taxonomy learning items: "
            f"{taxonomy_items.count()}"
        )

        self.stdout.write(
            f"Taxonomy question links: "
            f"{taxonomy_links.count()}"
        )

        self.stdout.write(
            f"Topic-tagged questions missing links: "
            f"{len(missing_topic_links)}"
        )

        self.stdout.write(
            f"Invalid topic links: "
            f"{invalid_topic_links}"
        )

        self.stdout.write(
            f"Invalid domain links: "
            f"{invalid_domain_links}"
        )

        self.stdout.write(
            f"Duplicate link pairs: "
            f"{duplicate_pairs}"
        )

        if missing_topic_links:
            errors.append(
                "Some topic-tagged eligible questions "
                "are not linked."
            )

        if invalid_topic_links:
            errors.append(
                "Some taxonomy links have topic mismatch."
            )

        if invalid_domain_links:
            errors.append(
                "Some taxonomy links have domain mismatch."
            )

        if duplicate_pairs:
            errors.append(
                "Duplicate LearningItemQuestion pairs exist."
            )

        self.stdout.write("")
        self.stdout.write(
            "READINESS SUMMARY"
        )

        if errors:

            for error in errors:
                self.stdout.write(
                    self.style.ERROR(
                        f"[FAIL] {error}"
                    )
                )

            raise SystemExit(1)

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Exact taxonomy linking is consistent."
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"[INFO] {untagged_questions.count()} "
                "eligible Aerospace questions still "
                "require topic classification before "
                "exact adaptive linking."
            )
        )