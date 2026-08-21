from django.core.management.base import (
    BaseCommand,
)

from assessment.models import Question

from learning.models import (
    CourseModule,
    LearningCourse,
    LearningItem,
    LearningProgram,
    PlacementQuestion,
)


class Command(BaseCommand):

    help = (
        "Audit AeroESP question-bank, "
        "placement, and learning-content readiness."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        self.stdout.write(
            "\nAeroESP Content Readiness\n"
        )

        self.stdout.write(
            "=" * 60
        )

        # -----------------------------------------
        # Question Bank
        # -----------------------------------------

        general_questions = (
            Question.objects.filter(
                track=(
                    Question.Track
                    .GENERAL_ENGLISH
                )
            )
        )

        aerospace_questions = (
            Question.objects.filter(
                track=(
                    Question.Track
                    .AEROSPACE_ESP
                )
            )
        )

        self.stdout.write(
            "\nQUESTION BANK"
        )

        self.stdout.write(
            f"General English questions: "
            f"{general_questions.count()}"
        )

        self.stdout.write(
            f"Aerospace ESP questions: "
            f"{aerospace_questions.count()}"
        )

        for skill_value, skill_label in (
            Question.Skill.choices
        ):

            general_count = (
                general_questions.filter(
                    skill=skill_value
                ).count()
            )

            aerospace_count = (
                aerospace_questions.filter(
                    skill=skill_value
                ).count()
            )

            self.stdout.write(
                f"  {skill_label:<15} "
                f"General={general_count:<4} "
                f"Aerospace={aerospace_count:<4}"
            )

        # -----------------------------------------
        # Placement
        # -----------------------------------------

        self.stdout.write(
            "\nPLACEMENT BANK"
        )

        placement_skills = [
            Question.Skill.VOCABULARY,
            Question.Skill.GRAMMAR,
            Question.Skill.READING,
            Question.Skill.LISTENING,
        ]

        placement_ready = True

        for skill in placement_skills:

            count = (
                PlacementQuestion.objects
                .filter(
                    is_active=True,
                    question__skill=skill,
                )
                .count()
            )

            status = (
                "READY"
                if count >= 10
                else "NEEDS CONTENT"
            )

            if count < 10:
                placement_ready = False

            self.stdout.write(
                f"  {skill:<12}: "
                f"{count:>3} / 10 minimum "
                f"[{status}]"
            )

        # -----------------------------------------
        # Programs / Courses / Modules
        # -----------------------------------------

        self.stdout.write(
            "\nLEARNING STRUCTURE"
        )

        self.stdout.write(
            f"Programs: "
            f"{LearningProgram.objects.count()}"
        )

        self.stdout.write(
            f"Courses: "
            f"{LearningCourse.objects.count()}"
        )

        self.stdout.write(
            f"Modules: "
            f"{CourseModule.objects.count()}"
        )

        self.stdout.write(
            f"Learning items: "
            f"{LearningItem.objects.count()}"
        )

        empty_modules = (
            CourseModule.objects
            .filter(items__isnull=True)
            .distinct()
        )

        self.stdout.write(
            f"Modules without content: "
            f"{empty_modules.count()}"
        )

        if empty_modules.exists():

            for module in (
                empty_modules
                .select_related(
                    "course",
                    "course__program",
                )
                .order_by(
                    "course__program",
                    "course",
                    "order",
                )
            ):

                self.stdout.write(
                    "  - "
                    f"{module.course.program} / "
                    f"{module.course} / "
                    f"{module.title}"
                )

        # -----------------------------------------
        # Result
        # -----------------------------------------

        self.stdout.write(
            "\nREADINESS SUMMARY"
        )

        if placement_ready:

            self.stdout.write(
                self.style.SUCCESS(
                    "[PASS] Placement bank "
                    "minimum reached."
                )
            )

        else:

            self.stdout.write(
                self.style.WARNING(
                    "[WARN] Placement bank "
                    "needs additional questions."
                )
            )

        if empty_modules.exists():

            self.stdout.write(
                self.style.WARNING(
                    "[WARN] Some learning modules "
                    "still have no content."
                )
            )

        else:

            self.stdout.write(
                self.style.SUCCESS(
                    "[PASS] Every learning module "
                    "has content."
                )
            )