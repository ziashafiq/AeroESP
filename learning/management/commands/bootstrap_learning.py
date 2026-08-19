from django.contrib.auth import (
    get_user_model,
)
from django.core.management.base import (
    BaseCommand,
)

from learning.models import (
    CourseModule,
    LearningCourse,
    LearningProgram,
)


class Command(BaseCommand):

    help = (
        "Create initial AeroESP "
        "learning programs and courses."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        User = get_user_model()

        owner = (
            User.objects
            .filter(
                is_superuser=True
            )
            .order_by(
                "id"
            )
            .first()
        )

        if owner is None:
            self.stdout.write(
                self.style.ERROR(
                    "No superuser exists."
                )
            )
            return

        ielts_program, _ = (
            LearningProgram.objects
            .get_or_create(
                code="ielts-general",
                defaults={
                    "title": (
                        "General English "
                        "& IELTS"
                    ),
                    "title_fa": (
                        "زبان عمومی و آیلتس"
                    ),
                    "program_type": (
                        LearningProgram
                        .ProgramType
                        .IELTS
                    ),
                    "description": (
                        "General English "
                        "learning and IELTS "
                        "preparation."
                    ),
                    "order": 1,
                },
            )
        )

        esp_program, _ = (
            LearningProgram.objects
            .get_or_create(
                code="aerospace-esp",
                defaults={
                    "title": (
                        "Aerospace English "
                        "& ESP"
                    ),
                    "title_fa": (
                        "زبان تخصصی هوافضا"
                    ),
                    "program_type": (
                        LearningProgram
                        .ProgramType
                        .AEROSPACE_ESP
                    ),
                    "description": (
                        "Specialized English "
                        "for aerospace "
                        "engineering."
                    ),
                    "order": 2,
                },
            )
        )

        ielts_course, _ = (
            LearningCourse.objects
            .get_or_create(
                code="ielts-foundation",
                defaults={
                    "program": (
                        ielts_program
                    ),
                    "title": (
                        "IELTS Foundation"
                    ),
                    "title_fa": (
                        "پایه آیلتس"
                    ),
                    "level": (
                        LearningCourse
                        .Level
                        .IELTS_5
                    ),
                    "description": (
                        "Vocabulary, grammar, "
                        "reading, listening, "
                        "writing and speaking."
                    ),
                    "order": 1,
                    "created_by": owner,
                },
            )
        )

        esp_course, _ = (
            LearningCourse.objects
            .get_or_create(
                code="aerospace-english-foundation",
                defaults={
                    "program": (
                        esp_program
                    ),
                    "title": (
                        "Aerospace English "
                        "Foundation"
                    ),
                    "title_fa": (
                        "پایه زبان تخصصی "
                        "مهندسی هوافضا"
                    ),
                    "level": (
                        LearningCourse
                        .Level
                        .ESP_FOUNDATION
                    ),
                    "description": (
                        "Core aerospace "
                        "vocabulary, reading "
                        "and technical "
                        "language."
                    ),
                    "order": 1,
                    "created_by": owner,
                },
            )
        )

        ielts_modules = [
            (
                "Vocabulary",
                CourseModule.ModuleType
                .VOCABULARY,
            ),
            (
                "Grammar",
                CourseModule.ModuleType
                .GRAMMAR,
            ),
            (
                "Reading",
                CourseModule.ModuleType
                .READING,
            ),
            (
                "Listening",
                CourseModule.ModuleType
                .LISTENING,
            ),
            (
                "Writing",
                CourseModule.ModuleType
                .WRITING,
            ),
            (
                "Speaking",
                CourseModule.ModuleType
                .SPEAKING,
            ),
            (
                "Review",
                CourseModule.ModuleType
                .REVIEW,
            ),
        ]

        for index, (
            title,
            module_type,
        ) in enumerate(
            ielts_modules,
            start=1,
        ):

            CourseModule.objects.get_or_create(
                course=ielts_course,
                order=index,
                defaults={
                    "title": title,
                    "module_type": (
                        module_type
                    ),
                },
            )

        esp_modules = [
            "General Aerospace",
            "Aerodynamics",
            "Flight Dynamics & Control",
            "Propulsion",
            "Structures",
            "Space & Satellite",
            "Technical Reading",
            "Technical Writing",
        ]

        for index, title in enumerate(
            esp_modules,
            start=1,
        ):

            CourseModule.objects.get_or_create(
                course=esp_course,
                order=index,
                defaults={
                    "title": title,
                    "module_type": (
                        CourseModule
                        .ModuleType
                        .ESP_TOPIC
                    ),
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "AeroESP Learning "
                "bootstrap: PASS"
            )
        )