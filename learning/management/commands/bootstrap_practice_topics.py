from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model

from assessment.models import (
    AerospaceDomain,
    Question,
)

from learning.models import (
    LearningProgram,
    LearningCourse,
    CourseModule,
    LearningItem,
)


class Command(BaseCommand):

    help = (
        "Create missing Aerospace ESP domain modules and "
        "topic-based public learning items used by the "
        "approved/demo aerospace question bank."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--apply",
            action="store_true",
            help="Persist changes. Default is dry-run.",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        apply_changes = options["apply"]

        # -------------------------------------------------
        # Locate Aerospace ESP course
        # -------------------------------------------------

        courses = (
            LearningCourse.objects
            .filter(
                program__program_type=(
                    LearningProgram
                    .ProgramType
                    .AEROSPACE_ESP
                ),
                is_active=True,
            )
            .select_related("program")
            .order_by("order", "pk")
        )

        if not courses.exists():
            raise CommandError(
                "No active Aerospace ESP course exists."
            )

        course = courses.first()

        # LearningItem.created_by is required.
        creator = course.created_by

        if creator is None:

            User = get_user_model()

            creator = (
                User.objects
                .filter(is_superuser=True)
                .order_by("pk")
                .first()
            )

        if creator is None:
            raise CommandError(
                "No valid creator is available."
            )

        # -------------------------------------------------
        # Only topics actually used by eligible questions
        # -------------------------------------------------

        topic_rows = (
            Question.objects
            .filter(
                track="AEROSPACE_ESP",
                status__in=[
                    "APPROVED",
                    "DEMO",
                ],
                topic_ref__isnull=False,
                topic_ref__is_active=True,
                domain_ref__isnull=False,
                domain_ref__is_active=True,
            )
            .exclude(
                visibility="EXAM_ONLY",
            )
            .values_list(
                "topic_ref_id",
                flat=True,
            )
            .distinct()
        )

        from assessment.models import AerospaceTopic

        topics = (
            AerospaceTopic.objects
            .filter(
                pk__in=topic_rows,
                is_active=True,
                domain__is_active=True,
            )
            .select_related("domain")
            .order_by(
                "domain__order",
                "order",
                "name",
            )
        )

        # -------------------------------------------------
        # Counters
        # -------------------------------------------------

        modules_to_create = 0
        modules_existing = 0

        items_to_create = 0
        items_existing = 0

        topic_count = topics.count()

        sample_actions = []

        # -------------------------------------------------
        # Process each domain represented in used topics
        # -------------------------------------------------

        domain_ids = (
            topics
            .values_list(
                "domain_id",
                flat=True,
            )
            .distinct()
        )

        domains = (
            AerospaceDomain.objects
            .filter(
                pk__in=domain_ids,
                is_active=True,
            )
            .order_by(
                "order",
                "name",
            )
        )

        domain_modules = {}

        next_order = (
            CourseModule.objects
            .filter(course=course)
            .order_by("-order")
            .values_list("order", flat=True)
            .first()
            or 0
        )

        for domain in domains:

            module = (
                CourseModule.objects
                .filter(
                    course=course,
                    aerospace_domain=domain,
                    is_active=True,
                )
                .first()
            )

            if module is not None:

                modules_existing += 1
                domain_modules[domain.pk] = module
                continue

            modules_to_create += 1
            next_order += 1

            if apply_changes:

                module = CourseModule.objects.create(
                    course=course,
                    aerospace_domain=domain,
                    title=domain.name,
                    title_fa="",
                    module_type="ESP_TOPIC",
                    description=(
                        "Aerospace ESP learning module "
                        f"for {domain.name}."
                    ),
                    order=next_order,
                    is_active=True,
                )

                domain_modules[domain.pk] = module

            if len(sample_actions) < 20:

                sample_actions.append(
                    (
                        "CREATE MODULE",
                        domain.pk,
                        domain.name,
                    )
                )

        # -------------------------------------------------
        # Dry-run needs virtual mapping for missing modules
        # -------------------------------------------------

        for topic in topics:

            existing_item = (
                LearningItem.objects
                .filter(
                    aerospace_topic=topic,
                    is_public=True,
                )
                .first()
            )

            if existing_item:

                items_existing += 1
                continue

            items_to_create += 1

            module = domain_modules.get(
                topic.domain_id
            )

            if apply_changes:

                if module is None:
                    raise CommandError(
                        "Expected domain module "
                        f"for topic {topic.name}."
                    )

                LearningItem.objects.create(
                    module=module,
                    aerospace_domain=topic.domain,
                    aerospace_topic=topic,
                    english_focus="",
                    english_topic="",
                    created_by=creator,
                    title=topic.name,
                    item_type="TECHNICAL_TERM",
                    meaning_fa="",
                    definition_en=(
                        "Practice and learning topic "
                        f"for {topic.name}."
                    ),
                    explanation=(
                        "This learning item organizes "
                        "AeroESP practice questions "
                        f"for the topic: {topic.name}."
                    ),
                    example="",
                    common_mistake="",
                    correct_form="",
                    source_type="COURSE",
                    source_reference=(
                        "AeroESP taxonomy-based "
                        "practice bootstrap"
                    ),
                    tags=[
                        "aerospace",
                        "esp",
                        topic.domain.code,
                        topic.code,
                    ],
                    is_verified=True,
                    is_public=True,
                )

            if len(sample_actions) < 20:

                sample_actions.append(
                    (
                        "CREATE ITEM",
                        topic.pk,
                        topic.name,
                        topic.domain.name,
                    )
                )

        # -------------------------------------------------
        # Dry-run rollback
        # -------------------------------------------------

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
            f"Course: {course.title}"
        )

        self.stdout.write(
            f"Used eligible topics: {topic_count}"
        )

        self.stdout.write(
            f"Existing domain modules: "
            f"{modules_existing}"
        )

        self.stdout.write(
            f"Missing domain modules: "
            f"{modules_to_create}"
        )

        self.stdout.write(
            f"Existing topic items: "
            f"{items_existing}"
        )

        self.stdout.write(
            f"Topic items to create: "
            f"{items_to_create}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Sample actions:"
        )

        for action in sample_actions:
            self.stdout.write(
                f"  {action}"
            )

        if apply_changes:

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Practice-topic bootstrap completed."
                )
            )

        else:

            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Dry run only. "
                    "No database changes saved."
                )
            )