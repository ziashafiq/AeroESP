from django.core.management.base import BaseCommand

from assessment.models import Question


class Command(BaseCommand):
    help = "Load the AeroESP prototype question dataset."

    def handle(self, *args, **options):

        # Delete existing questions so the prototype dataset is reproducible.
        Question.objects.all().delete()

        questions = [

            # =========================================================
            # TECHNICAL VOCABULARY
            # =========================================================

            Question(
                question_text=(
                    "When the angle of attack exceeds its critical value, "
                    "the airflow may ___ from the upper surface of the wing."
                ),
                option_a="accelerate",
                option_b="separate",
                option_c="stabilize",
                option_d="compress",
                correct_answer="B",
                skill=Question.Skill.VOCABULARY,
                aerospace_domain=Question.Domain.AERODYNAMICS,
                difficulty=Question.Difficulty.BASIC,
                explanation=(
                    "At a sufficiently high angle of attack, boundary-layer "
                    "separation can occur and may lead to stall."
                ),
            ),

            Question(
                question_text=(
                    "The rotation of an aircraft about its lateral axis "
                    "is called ___."
                ),
                option_a="yaw",
                option_b="roll",
                option_c="pitch",
                option_d="sideslip",
                correct_answer="C",
                skill=Question.Skill.VOCABULARY,
                aerospace_domain=Question.Domain.FLIGHT_DYNAMICS,
                difficulty=Question.Difficulty.BASIC,
                explanation=(
                    "Pitch is the rotation of an aircraft about its lateral axis."
                ),
            ),

            Question(
                question_text=(
                    "In a gas-turbine engine, the component that increases "
                    "the pressure of the incoming air before combustion "
                    "is the ___."
                ),
                option_a="nozzle",
                option_b="compressor",
                option_c="turbine",
                option_d="exhaust duct",
                correct_answer="B",
                skill=Question.Skill.VOCABULARY,
                aerospace_domain=Question.Domain.PROPULSION,
                difficulty=Question.Difficulty.BASIC,
                explanation=(
                    "The compressor raises the pressure of the incoming air "
                    "before it enters the combustor."
                ),
            ),

            Question(
                question_text=(
                    "The drag associated with the production of lift and "
                    "the trailing vortex system is called ___."
                ),
                option_a="wave drag",
                option_b="skin-friction drag",
                option_c="induced drag",
                option_d="base drag",
                correct_answer="C",
                skill=Question.Skill.VOCABULARY,
                aerospace_domain=Question.Domain.AERODYNAMICS,
                difficulty=Question.Difficulty.INTERMEDIATE,
                explanation=(
                    "Induced drag is a consequence of producing lift and "
                    "is associated with the trailing vortex system."
                ),
            ),

            # =========================================================
            # GRAMMAR IN ENGINEERING CONTEXT
            # =========================================================

            Question(
                question_text=(
                    "As airspeed increases, the dynamic pressure ___."
                ),
                option_a="increase",
                option_b="increases",
                option_c="increased",
                option_d="increasing",
                correct_answer="B",
                skill=Question.Skill.GRAMMAR,
                aerospace_domain=Question.Domain.AERODYNAMICS,
                difficulty=Question.Difficulty.BASIC,
                explanation=(
                    "The singular subject 'dynamic pressure' requires "
                    "the verb 'increases' in the present simple."
                ),
            ),

            Question(
                question_text=(
                    "If the aircraft ___ dynamically stable, the oscillations "
                    "will gradually decrease with time."
                ),
                option_a="is",
                option_b="was",
                option_c="were",
                option_d="has been",
                correct_answer="A",
                skill=Question.Skill.GRAMMAR,
                aerospace_domain=Question.Domain.FLIGHT_DYNAMICS,
                difficulty=Question.Difficulty.BASIC,
                explanation=(
                    "This is a first conditional structure: "
                    "if + present simple, followed by will + base verb."
                ),
            ),

            Question(
                question_text=(
                    "The incoming air ___ in the compressor before "
                    "it enters the combustion chamber."
                ),
                option_a="compresses",
                option_b="compressed",
                option_c="is compressed",
                option_d="has compress",
                correct_answer="C",
                skill=Question.Skill.GRAMMAR,
                aerospace_domain=Question.Domain.PROPULSION,
                difficulty=Question.Difficulty.INTERMEDIATE,
                explanation=(
                    "A passive construction is required because the air "
                    "receives the action: 'is compressed'."
                ),
            ),

            Question(
                question_text=(
                    "Had the damping ratio been higher, the oscillations "
                    "___ more rapidly."
                ),
                option_a="decay",
                option_b="will decay",
                option_c="would have decayed",
                option_d="have decayed",
                correct_answer="C",
                skill=Question.Skill.GRAMMAR,
                aerospace_domain=Question.Domain.FLIGHT_DYNAMICS,
                difficulty=Question.Difficulty.ADVANCED,
                explanation=(
                    "'Had ... been' is an inverted third conditional and "
                    "requires 'would have + past participle'."
                ),
            ),

            # =========================================================
            # TECHNICAL READING
            # =========================================================

            Question(
                question_text=(
                    "Read the passage:\n\n"
                    "For a conventional wing at low Mach number, lift generally "
                    "increases with angle of attack over the approximately "
                    "linear portion of the lift curve. Beyond a critical angle, "
                    "extensive flow separation occurs and the lift coefficient "
                    "can decrease.\n\n"
                    "According to the passage, what happens after the critical "
                    "angle of attack is exceeded?"
                ),
                option_a="Lift necessarily continues to increase linearly.",
                option_b="Flow separation can increase and lift may decrease.",
                option_c="Drag becomes zero.",
                option_d="The wing produces no aerodynamic force.",
                correct_answer="B",
                skill=Question.Skill.READING,
                aerospace_domain=Question.Domain.AERODYNAMICS,
                difficulty=Question.Difficulty.INTERMEDIATE,
                explanation=(
                    "The passage states that extensive separation occurs "
                    "beyond the critical angle and the lift coefficient may decrease."
                ),
            ),

            Question(
                question_text=(
                    "Read the passage:\n\n"
                    "An aircraft may initially tend to return toward its trim "
                    "condition after a small disturbance, indicating positive "
                    "static stability. However, if the amplitude of the resulting "
                    "oscillations grows with time, the aircraft is dynamically "
                    "unstable.\n\n"
                    "Which statement best describes this aircraft?"
                ),
                option_a="Statically unstable and dynamically stable",
                option_b="Statically stable and dynamically unstable",
                option_c="Both statically and dynamically stable",
                option_d="Neither static nor dynamic behavior can be inferred",
                correct_answer="B",
                skill=Question.Skill.READING,
                aerospace_domain=Question.Domain.FLIGHT_DYNAMICS,
                difficulty=Question.Difficulty.INTERMEDIATE,
                explanation=(
                    "The initial restoring tendency indicates positive static "
                    "stability, while growing oscillations indicate dynamic instability."
                ),
            ),

            Question(
                question_text=(
                    "Read the passage:\n\n"
                    "A turbofan engine produces thrust by accelerating both "
                    "the air passing through the engine core and a larger mass "
                    "of air flowing around the core through the bypass duct. "
                    "In high-bypass turbofan engines, a significant portion of "
                    "the total thrust is produced by the bypass flow.\n\n"
                    "What is an important characteristic of a high-bypass "
                    "turbofan engine?"
                ),
                option_a="All thrust is generated by the engine core.",
                option_b="A significant portion of thrust is generated by bypass airflow.",
                option_c="It operates without a fan.",
                option_d="The bypass flow produces no thrust.",
                correct_answer="B",
                skill=Question.Skill.READING,
                aerospace_domain=Question.Domain.PROPULSION,
                difficulty=Question.Difficulty.INTERMEDIATE,
                explanation=(
                    "The passage explicitly states that a significant portion "
                    "of thrust comes from the bypass flow."
                ),
            ),

            Question(
                question_text=(
                    "Read the passage:\n\n"
                    "In a converging propulsion nozzle operating under appropriate "
                    "conditions, the flow accelerates as it approaches the exit. "
                    "The nozzle converts part of the flow's pressure and thermal "
                    "energy into directed kinetic energy, contributing to the "
                    "generation of thrust.\n\n"
                    "What is the principal function described for the nozzle?"
                ),
                option_a="To store fuel",
                option_b="To reduce all flow velocity",
                option_c="To convert available flow energy into directed kinetic energy",
                option_d="To increase aircraft mass",
                correct_answer="C",
                skill=Question.Skill.READING,
                aerospace_domain=Question.Domain.PROPULSION,
                difficulty=Question.Difficulty.INTERMEDIATE,
                explanation=(
                    "The passage describes the conversion of available flow energy "
                    "into directed kinetic energy."
                ),
            ),
        ]

        Question.objects.bulk_create(questions)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully loaded {len(questions)} AeroESP questions."
            )
        )