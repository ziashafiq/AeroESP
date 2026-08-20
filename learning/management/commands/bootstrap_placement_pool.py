from django.core.management.base import BaseCommand

from assessment.models import Question
from learning.models import (
    LearningProgram,
    PlacementQuestion,
)


class Command(BaseCommand):

    help = (
        "Build the General English placement "
        "pool from the central Question Bank."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        program = (
            LearningProgram.objects.get(
                program_type=(
                    LearningProgram
                    .ProgramType
                    .IELTS
                )
            )
        )

        skills = [
            Question.Skill.VOCABULARY,
            Question.Skill.GRAMMAR,
            Question.Skill.READING,
            Question.Skill.LISTENING,
        ]

        order = 1
        created_count = 0

        for skill in skills:

            questions = (
                Question.objects
                .filter(
                    track=(
                        Question.Track
                        .GENERAL_ENGLISH
                    ),
                    skill=skill,
                )
                .order_by(
                    "pk",
                )[:10]
            )

            for question in questions:

                _, created = (
                    PlacementQuestion.objects
                    .get_or_create(
                        program=program,
                        question=question,
                        defaults={
                            "order": order,
                        },
                    )
                )

                if created:
                    created_count += 1

                order += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Placement pool ready. "
                f"New links: {created_count}. "
                f"Total: "
                f"{PlacementQuestion.objects.filter(program=program).count()}"
            )
        )