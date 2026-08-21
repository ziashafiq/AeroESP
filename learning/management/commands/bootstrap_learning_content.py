from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from learning.models import (
    CourseModule,
    LearningItem,
)


SOURCE_REFERENCE = (
    "AeroESP Learning Starter v1"
)


STARTER_CONTENT = {

    # =====================================================
    # GENERAL ENGLISH / IELTS
    # =====================================================

    "Vocabulary": {
        "title": "Core academic vocabulary",
        "item_type": LearningItem.ItemType.WORD,
        "english_topic": "Academic Vocabulary",
        "definition_en": (
            "High-frequency vocabulary used in "
            "academic and professional English."
        ),
        "explanation": (
            "Learn meaning, usage, and context "
            "rather than memorizing isolated words."
        ),
        "example": (
            "The results show a significant improvement."
        ),
    },

    "Grammar": {
        "title": "Present simple agreement",
        "item_type": (
            LearningItem.ItemType.GRAMMAR_RULE
        ),
        "english_topic": "Present Simple",
        "definition_en": (
            "In the present simple, third-person "
            "singular subjects normally take a verb "
            "ending in -s or -es."
        ),
        "explanation": (
            "Use this structure for facts, routines, "
            "and repeated actions."
        ),
        "example": (
            "The student studies English every day."
        ),
    },

    "Reading": {
        "title": "Finding the main idea",
        "item_type": (
            LearningItem.ItemType.READING_NOTE
        ),
        "english_topic": "Main Idea",
        "definition_en": (
            "The main idea expresses the central "
            "message of a paragraph or passage."
        ),
        "explanation": (
            "Identify repeated concepts and distinguish "
            "the central point from supporting details."
        ),
        "example": (
            "Ask: What is the writer mainly saying?"
        ),
    },

    "Listening": {
        "title": "Listening for key details",
        "item_type": (
            LearningItem.ItemType.LISTENING_NOTE
        ),
        "english_topic": "Key Details",
        "definition_en": (
            "Key-detail listening focuses on information "
            "such as time, place, number, reason, "
            "and action."
        ),
        "explanation": (
            "Listen for meaning rather than trying "
            "to recognize every individual word."
        ),
        "example": (
            "Listen specifically for the meeting time."
        ),
    },

    "Writing": {
        "title": "Writing a clear topic sentence",
        "item_type": (
            LearningItem.ItemType.WRITING_PATTERN
        ),
        "english_topic": "Paragraph Writing",
        "definition_en": (
            "A topic sentence introduces the main "
            "idea developed in a paragraph."
        ),
        "explanation": (
            "Keep it focused enough that the remaining "
            "sentences can support it clearly."
        ),
        "example": (
            "Online learning provides students "
            "with greater scheduling flexibility."
        ),
    },

    "Speaking": {
        "title": "Structuring a spoken response",
        "item_type": (
            LearningItem.ItemType.SPEAKING_PATTERN
        ),
        "english_topic": "Structured Response",
        "definition_en": (
            "A clear spoken response can follow "
            "answer, reason, and example."
        ),
        "explanation": (
            "This structure helps learners produce "
            "coherent answers instead of isolated "
            "sentences."
        ),
        "example": (
            "I prefer online learning because it is "
            "flexible. For example, I can study "
            "after work."
        ),
    },

    "Review": {
        "title": "Spaced review strategy",
        "item_type": LearningItem.ItemType.OTHER,
        "english_topic": "Review Strategy",
        "definition_en": (
            "Spaced review revisits learning material "
            "after increasing intervals."
        ),
        "explanation": (
            "Review weak and due material regularly "
            "instead of repeating only new content."
        ),
        "example": (
            "Review a difficult item today, then again "
            "after several days."
        ),
    },

    # =====================================================
    # AEROSPACE ESP
    # =====================================================

    "General Aerospace": {
        "title": "Aircraft",
        "item_type": (
            LearningItem.ItemType.TECHNICAL_TERM
        ),
        "english_topic": "",
        "definition_en": (
            "An aircraft is a vehicle designed "
            "for flight in the atmosphere."
        ),
        "explanation": (
            "Aircraft is a general technical term "
            "covering airplanes, helicopters, "
            "and other atmospheric flight vehicles."
        ),
        "example": (
            "The aircraft begins its climb after takeoff."
        ),
    },

    "Aerodynamics": {
        "title": "Boundary layer",
        "item_type": (
            LearningItem.ItemType.TECHNICAL_TERM
        ),
        "english_topic": "",
        "definition_en": (
            "The boundary layer is the near-wall "
            "region of a fluid flow where viscous "
            "effects are significant."
        ),
        "explanation": (
            "Boundary-layer behavior is important "
            "when discussing drag and flow separation."
        ),
        "example": (
            "An adverse pressure gradient may cause "
            "boundary-layer separation."
        ),
    },

    "Flight Dynamics & Control": {
        "title": "Static stability",
        "item_type": (
            LearningItem.ItemType.TECHNICAL_TERM
        ),
        "english_topic": "",
        "definition_en": (
            "Static stability describes the initial "
            "tendency of an aircraft after a disturbance "
            "from equilibrium."
        ),
        "explanation": (
            "A statically stable aircraft initially "
            "tends to return toward its equilibrium "
            "condition."
        ),
        "example": (
            "Longitudinal static stability is strongly "
            "related to pitching-moment behavior."
        ),
    },

    "Propulsion": {
        "title": "Thrust",
        "item_type": (
            LearningItem.ItemType.TECHNICAL_TERM
        ),
        "english_topic": "",
        "definition_en": (
            "Thrust is the propulsive force produced "
            "to move an aircraft or propulsion system "
            "forward."
        ),
        "explanation": (
            "In flight-performance discussions, "
            "thrust is commonly compared with drag."
        ),
        "example": (
            "For steady level flight, thrust balances "
            "drag under idealized conditions."
        ),
    },

    "Structures": {
        "title": "Structural load",
        "item_type": (
            LearningItem.ItemType.TECHNICAL_TERM
        ),
        "english_topic": "",
        "definition_en": (
            "A structural load is a force or moment "
            "applied to an aircraft structural component."
        ),
        "explanation": (
            "Aircraft structures are designed to "
            "carry aerodynamic, inertial, and other "
            "operational loads."
        ),
        "example": (
            "The wing structure must withstand "
            "significant bending loads."
        ),
    },

    "Space & Satellite": {
        "title": "Orbit",
        "item_type": (
            LearningItem.ItemType.TECHNICAL_TERM
        ),
        "english_topic": "",
        "definition_en": (
            "An orbit is the trajectory of an object "
            "moving around another body primarily "
            "under gravitational influence."
        ),
        "explanation": (
            "Orbital terminology is fundamental "
            "to satellite and space-system English."
        ),
        "example": (
            "The satellite was inserted into "
            "a low Earth orbit."
        ),
    },

    "Technical Reading": {
        "title": "Reading technical definitions",
        "item_type": (
            LearningItem.ItemType.READING_NOTE
        ),
        "english_topic": "",
        "definition_en": (
            "Technical definitions identify a term "
            "and state the properties that distinguish "
            "its engineering meaning."
        ),
        "explanation": (
            "Look for patterns such as "
            "'is defined as', 'refers to', "
            "and 'is characterized by'."
        ),
        "example": (
            "Lift is defined as the aerodynamic force "
            "component perpendicular to the relative flow."
        ),
    },

    "Technical Writing": {
        "title": "Writing cause-and-effect statements",
        "item_type": (
            LearningItem.ItemType.WRITING_PATTERN
        ),
        "english_topic": "",
        "definition_en": (
            "Cause-and-effect structures explain how "
            "one engineering condition produces "
            "or influences another."
        ),
        "explanation": (
            "Useful connectors include because, "
            "therefore, consequently, results in, "
            "and leads to."
        ),
        "example": (
            "An increase in angle of attack may lead "
            "to higher lift before stall."
        ),
    },
}


FOCUS_BY_MODULE_TYPE = {
    "VOCABULARY": "VOCAB",
    "GRAMMAR": "GRAMMAR",
    "READING": "READING",
    "LISTENING": "LISTENING",
    "WRITING": "WRITING",
    "SPEAKING": "SPEAKING",
    "REVIEW": "VOCAB",
}


class Command(BaseCommand):

    help = (
        "Create idempotent starter LearningItems "
        "for AeroESP learning modules."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        created = 0
        skipped = 0
        missing = 0

        modules = (
            CourseModule.objects
            .select_related(
                "course",
                "course__program",
                "course__created_by",
                "aerospace_domain",
            )
            .filter(
                is_active=True
            )
            .order_by(
                "course__order",
                "order",
            )
        )

        for module in modules:

            # Existing real content always wins.
            if module.items.exists():

                skipped += 1

                self.stdout.write(
                    f"[SKIP] {module.course.title}"
                    f" / {module.title}"
                    " already has content."
                )

                continue

            payload = STARTER_CONTENT.get(
                module.title
            )

            if payload is None:

                missing += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"[WARN] No starter payload for "
                        f"{module.course.title}"
                        f" / {module.title}"
                    )
                )

                continue

            creator = (
                module.course.created_by
            )

            if creator is None:

                raise CommandError(
                    f"Course {module.course_id} "
                    "has no creator."
                )

            program_type = (
                module.course
                .program
                .program_type
            )

            is_aerospace = (
                program_type
                == "AEROSPACE_ESP"
            )

            focus_candidate = (
                FOCUS_BY_MODULE_TYPE.get(
                    module.module_type,
                    "",
                )
            )

            # Simplified: set english_focus to focus_candidate
            # only if not aerospace, otherwise empty string.
            english_focus = (
                ""
                if is_aerospace
                else focus_candidate
            )

            item, was_created = (
                LearningItem.objects
                .get_or_create(
                    module=module,
                    title=payload["title"],
                    source_reference=(
                        SOURCE_REFERENCE
                    ),
                    defaults={
                        "aerospace_domain": (
                            module.aerospace_domain
                            if is_aerospace
                            else None
                        ),
                        "aerospace_topic": None,
                        "english_focus": english_focus,
                        "english_topic": (
                            payload.get(
                                "english_topic",
                                "",
                            )
                        ),
                        "created_by": creator,
                        "item_type": (
                            payload["item_type"]
                        ),
                        "meaning_fa": "",
                        "definition_en": (
                            payload[
                                "definition_en"
                            ]
                        ),
                        "explanation": (
                            payload[
                                "explanation"
                            ]
                        ),
                        "example": (
                            payload["example"]
                        ),
                        "common_mistake": "",
                        "correct_form": "",
                        "source_type": (
                            LearningItem
                            .SourceType
                            .COURSE
                        ),
                        "tags": [
                            "starter",
                            "bootstrap",
                            (
                                "aerospace_esp"
                                if is_aerospace
                                else "general_english"
                            ),
                        ],
                        "is_verified": True,
                        "is_public": True,
                    },
                )
            )

            if was_created:

                created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[CREATE] "
                        f"{module.course.title}"
                        f" / {module.title}"
                        f" -> {item.title}"
                    )
                )

            else:

                skipped += 1

                self.stdout.write(
                    f"[SKIP] "
                    f"{module.course.title}"
                    f" / {module.title}"
                )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Learning starter content ready. "
                f"Created: {created}; "
                f"Skipped: {skipped}; "
                f"Missing: {missing}"
            )
        )

        if missing:

            raise CommandError(
                f"{missing} active module(s) "
                "have no starter payload."
            )