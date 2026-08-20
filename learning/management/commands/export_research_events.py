import csv
import hashlib
import hmac
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from learning.models import LearningEvent


class Command(BaseCommand):

    help = (
        "Export anonymized AeroESP "
        "learning-event research data."
    )

    def add_arguments(
        self,
        parser,
    ):

        parser.add_argument(
            "--output",
            default=(
                "research_exports/"
                "learning_events.csv"
            ),
        )

    def handle(
        self,
        *args,
        **options,
    ):

        output_path = Path(
            options["output"]
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        def anonymous_id(
            student_id,
        ):

            message = str(
                student_id
            ).encode("utf-8")

            key = (
                settings.SECRET_KEY
                .encode("utf-8")
            )

            digest = hmac.new(
                key,
                message,
                hashlib.sha256,
            ).hexdigest()

            return digest[:16]

        events = (
            LearningEvent.objects
            .select_related(
                "student",
                "learning_item",
                "question",
                "placement_attempt",
            )
            .order_by(
                "occurred_at",
                "pk",
            )
        )

        fields = [
            "event_id",
            "learner_id",
            "event_type",
            "occurred_at",
            "program_type",
            "skill",
            "aerospace_domain",
            "aerospace_topic",
            "english_focus",
            "english_topic",
            "question_id",
            "learning_item_id",
            "selected_answer",
            "correct_answer",
            "is_correct",
            "mastery_before",
            "mastery_after",
            "review_count_before",
            "review_count_after",
        ]

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields,
            )

            writer.writeheader()

            for event in events:

                writer.writerow(
                    {
                        "event_id": (
                            event.pk
                        ),
                        "learner_id": (
                            anonymous_id(
                                event.student_id
                            )
                        ),
                        "event_type": (
                            event.event_type
                        ),
                        "occurred_at": (
                            event.occurred_at
                            .isoformat()
                        ),
                        "program_type": (
                            event.program_type
                        ),
                        "skill": (
                            event.skill
                        ),
                        "aerospace_domain": (
                            event.aerospace_domain
                        ),
                        "aerospace_topic": (
                            event.aerospace_topic
                        ),
                        "english_focus": (
                            event.english_focus
                        ),
                        "english_topic": (
                            event.english_topic
                        ),
                        "question_id": (
                            event.question_id
                            or ""
                        ),
                        "learning_item_id": (
                            event.learning_item_id
                            or ""
                        ),
                        "selected_answer": (
                            event.selected_answer
                        ),
                        "correct_answer": (
                            event.correct_answer
                        ),
                        "is_correct": (
                            event.is_correct
                        ),
                        "mastery_before": (
                            event.mastery_before
                            if event.mastery_before
                            is not None
                            else ""
                        ),
                        "mastery_after": (
                            event.mastery_after
                            if event.mastery_after
                            is not None
                            else ""
                        ),
                        "review_count_before": (
                            event.review_count_before
                            if event.review_count_before
                            is not None
                            else ""
                        ),
                        "review_count_after": (
                            event.review_count_after
                            if event.review_count_after
                            is not None
                            else ""
                        ),
                    }
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Exported "
                f"{events.count()} events to "
                f"{output_path}"
            )
        )