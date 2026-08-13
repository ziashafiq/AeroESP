import random

from django.core.management.base import BaseCommand

from assessment.models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


TAXONOMY = {
    "GENERAL": {
        "name": "General Aerospace & Fundamentals",
        "order": 1,
        "topics": [
            ("FUNDAMENTALS", "Aerospace Fundamentals"),
            ("ATMOSPHERE", "Atmosphere"),
            ("AIRCRAFT_COMPONENTS", "Aircraft Components"),
            ("MISSION", "Mission Analysis"),
            ("WEIGHT_BALANCE", "Weight & Balance"),
            ("OPERATIONS", "Aircraft Operations"),
        ],
    },

    "AERO": {
        "name": "Aerodynamics & Fluid Mechanics",
        "order": 2,
        "topics": [
            ("AERO_FUND", "Aerodynamics Fundamentals"),
            ("BOUNDARY_LAYER", "Boundary Layer"),
            ("FLOW_SEPARATION", "Flow Separation"),
            ("COMPRESSIBLE", "Compressible Flow"),
            ("TURBULENCE", "Turbulence"),
            ("AIRFOILS", "Airfoils"),
            ("WINGS", "Wing Aerodynamics"),
            ("HIGH_SPEED", "High-Speed Aerodynamics"),
            ("CFD_AERO", "Computational Aerodynamics"),
        ],
    },

    "FLIGHT": {
        "name": "Flight Mechanics, Dynamics & Control",
        "order": 3,
        "topics": [
            ("FLIGHT_MECHANICS", "Flight Mechanics"),
            ("STATIC_STABILITY", "Static Stability"),
            ("DYNAMIC_STABILITY", "Dynamic Stability"),
            ("LONGITUDINAL", "Longitudinal Dynamics"),
            ("LATERAL", "Lateral-Directional Dynamics"),
            ("FLIGHT_CONTROL", "Flight Control"),
            ("AUTOPILOT", "Autopilot"),
            ("GUIDANCE", "Guidance"),
            ("NAVIGATION", "Navigation"),
            ("ROBUST_CONTROL", "Robust Control"),
            ("ADAPTIVE_CONTROL", "Adaptive Control"),
        ],
    },

    "PROP": {
        "name": "Propulsion & Power Systems",
        "order": 4,
        "topics": [
            ("PROP_FUND", "Propulsion Fundamentals"),
            ("GAS_TURBINE", "Gas Turbines"),
            ("TURBOJET", "Turbojet Engines"),
            ("TURBOFAN", "Turbofan Engines"),
            ("TURBOPROP", "Turboprop Engines"),
            ("ROCKET", "Rocket Propulsion"),
            ("ELECTRIC_PROP", "Electric Propulsion"),
            ("HYBRID_PROP", "Hybrid Propulsion"),
        ],
    },

    "STRUCT": {
        "name": "Structures & Materials",
        "order": 5,
        "topics": [
            ("STRUCT_MECH", "Structural Mechanics"),
            ("STRESS_STRAIN", "Stress & Strain"),
            ("BUCKLING", "Buckling"),
            ("FATIGUE", "Fatigue"),
            ("FRACTURE", "Fracture Mechanics"),
            ("COMPOSITES", "Composite Materials"),
            ("AEROELASTICITY", "Aeroelasticity"),
            ("VIBRATION", "Structural Vibration"),
        ],
    },

    "DESIGN": {
        "name": "Aircraft Design & Performance",
        "order": 6,
        "topics": [
            ("CONCEPTUAL_DESIGN", "Conceptual Design"),
            ("CONFIGURATION", "Aircraft Configuration"),
            ("WEIGHT_ESTIMATION", "Weight Estimation"),
            ("PERFORMANCE", "Aircraft Performance"),
            ("TAKEOFF", "Takeoff Performance"),
            ("LANDING", "Landing Performance"),
            ("RANGE", "Range"),
            ("ENDURANCE", "Endurance"),
            ("OPTIMIZATION", "Design Optimization"),
        ],
    },

    "AVIONICS": {
        "name": "Avionics, Navigation & Sensors",
        "order": 7,
        "topics": [
            ("AVIONICS_FUND", "Avionics Fundamentals"),
            ("INS", "Inertial Navigation"),
            ("GNSS", "GNSS"),
            ("RADAR", "Radar"),
            ("AIR_DATA", "Air Data Systems"),
            ("SENSORS", "Aircraft Sensors"),
            ("SENSOR_FUSION", "Sensor Fusion"),
            ("COMMUNICATION", "Aircraft Communication"),
        ],
    },

    "SPACE": {
        "name": "Space Engineering & Astronautics",
        "order": 8,
        "topics": [
            ("ORBITAL", "Orbital Mechanics"),
            ("SPACECRAFT_DYN", "Spacecraft Dynamics"),
            ("ATTITUDE", "Attitude Dynamics"),
            ("ADCS", "Attitude Determination & Control"),
            ("SPACE_PROP", "Space Propulsion"),
            ("LAUNCH", "Launch Vehicles"),
            ("SATELLITES", "Satellite Systems"),
            ("SPACE_MISSION", "Space Mission Design"),
        ],
    },

    "UAV": {
        "name": "UAV, Robotics & Autonomous Systems",
        "order": 9,
        "topics": [
            ("UAV_FUND", "UAV Fundamentals"),
            ("PATH_PLANNING", "Path Planning"),
            ("AUTONOMY", "Autonomous Flight"),
            ("OBSTACLE_AVOID", "Obstacle Avoidance"),
            ("SWARM", "Swarm Systems"),
            ("VISION", "Machine Vision"),
            ("ROBOTICS", "Aerial Robotics"),
            ("UAM", "Urban Air Mobility"),
            ("EVTOL", "eVTOL Systems"),
        ],
    },

    "SYSTEMS": {
        "name": "Systems Engineering, Safety & Reliability",
        "order": 10,
        "topics": [
            ("SYSTEMS_ENG", "Systems Engineering"),
            ("REQUIREMENTS", "Requirements Engineering"),
            ("RELIABILITY", "Reliability"),
            ("SAFETY", "Safety Engineering"),
            ("FMEA", "Failure Mode Analysis"),
            ("FAULT_TOLERANCE", "Fault-Tolerant Systems"),
            ("REDUNDANCY", "Redundancy"),
            ("RISK", "Risk Assessment"),
        ],
    },

    "MAINT": {
        "name": "Manufacturing, Maintenance & Airworthiness",
        "order": 11,
        "topics": [
            ("MANUFACTURING", "Aerospace Manufacturing"),
            ("MAINTENANCE", "Aircraft Maintenance"),
            ("NDT", "Non-Destructive Testing"),
            ("AIRWORTHINESS", "Airworthiness"),
            ("CERTIFICATION", "Certification"),
            ("INSPECTION", "Aircraft Inspection"),
            ("MRO", "Maintenance, Repair & Overhaul"),
        ],
    },

    "METHODS": {
        "name": "Experimental, Computational & Data Methods",
        "order": 12,
        "topics": [
            ("CFD", "Computational Fluid Dynamics"),
            ("FEM", "Finite Element Method"),
            ("WIND_TUNNEL", "Wind-Tunnel Testing"),
            ("FLIGHT_TEST", "Flight Testing"),
            ("SYSTEM_ID", "System Identification"),
            ("MONTE_CARLO", "Monte Carlo Methods"),
            ("DATA_ANALYSIS", "Engineering Data Analysis"),
            ("ML", "Machine Learning in Aerospace"),
            ("DIGITAL_TWIN", "Digital Twin"),
        ],
    },
}


# Exactly 50 concepts.
# Two questions are generated from each concept = 100 questions.
CONCEPTS = [
    ("GENERAL", "FUNDAMENTALS", "payload",
     "the useful load carried by an aircraft or spacecraft"),
    ("GENERAL", "MISSION", "mission profile",
     "the sequence of operating phases that defines a mission"),
    ("GENERAL", "WEIGHT_BALANCE", "center of gravity",
     "the point through which the resultant weight of a vehicle acts"),
    ("GENERAL", "ATMOSPHERE", "density altitude",
     "pressure altitude corrected for nonstandard temperature"),
    ("GENERAL", "OPERATIONS", "airworthiness",
     "the condition of being safe and suitable for flight"),
    ("GENERAL", "AIRCRAFT_COMPONENTS", "empennage",
     "the tail assembly of an aircraft"),

    ("AERO", "AERO_FUND", "lift coefficient",
     "a nondimensional measure of aerodynamic lift"),
    ("AERO", "AERO_FUND", "drag coefficient",
     "a nondimensional measure of aerodynamic drag"),
    ("AERO", "BOUNDARY_LAYER", "boundary layer",
     "the thin region near a surface where viscous effects are important"),
    ("AERO", "FLOW_SEPARATION", "flow separation",
     "the detachment of a boundary layer from a surface"),

    ("FLIGHT", "STATIC_STABILITY", "static stability",
     "the initial tendency of an aircraft after a disturbance"),
    ("FLIGHT", "DYNAMIC_STABILITY", "dynamic stability",
     "the time history of aircraft motion following a disturbance"),
    ("FLIGHT", "FLIGHT_MECHANICS", "trim",
     "a condition in which forces and moments are balanced"),
    ("FLIGHT", "LATERAL", "Dutch roll",
     "a coupled lateral-directional oscillatory aircraft mode"),

    ("PROP", "PROP_FUND", "thrust",
     "the propulsive force that accelerates a vehicle"),
    ("PROP", "GAS_TURBINE", "compressor",
     "the gas-turbine component that raises the pressure of incoming air"),
    ("PROP", "GAS_TURBINE", "turbine",
     "the component that extracts energy from hot expanding gas"),
    ("PROP", "ROCKET", "specific impulse",
     "a measure of rocket propulsion efficiency"),

    ("STRUCT", "STRESS_STRAIN", "stress",
     "internal force per unit area within a material"),
    ("STRUCT", "STRESS_STRAIN", "strain",
     "deformation normalized by the original dimension"),
    ("STRUCT", "FATIGUE", "fatigue",
     "progressive damage caused by repeated cyclic loading"),
    ("STRUCT", "BUCKLING", "buckling",
     "sudden structural instability under compressive loading"),

    ("DESIGN", "PERFORMANCE", "wing loading",
     "aircraft weight divided by wing reference area"),
    ("DESIGN", "CONCEPTUAL_DESIGN", "aspect ratio",
     "a measure relating wing span to wing area"),
    ("DESIGN", "RANGE", "range",
     "the maximum distance an aircraft can travel"),
    ("DESIGN", "ENDURANCE", "endurance",
     "the maximum time an aircraft can remain airborne"),

    ("AVIONICS", "INS", "inertial navigation",
     "navigation based on measured acceleration and angular motion"),
    ("AVIONICS", "GNSS", "GNSS",
     "satellite-based positioning and navigation"),
    ("AVIONICS", "AIR_DATA", "pitot-static system",
     "a system that measures pressures used to derive airspeed and altitude"),
    ("AVIONICS", "SENSOR_FUSION", "sensor fusion",
     "combining information from multiple sensors to improve estimation"),

    ("SPACE", "ORBITAL", "apogee",
     "the point in an orbit farthest from the central body"),
    ("SPACE", "ORBITAL", "perigee",
     "the point in an Earth orbit closest to Earth"),
    ("SPACE", "ORBITAL", "orbital inclination",
     "the angle between an orbital plane and a reference plane"),
    ("SPACE", "SPACE_MISSION", "delta-v",
     "the total change in velocity required for a maneuver or mission"),

    ("UAV", "PATH_PLANNING", "waypoint",
     "a predefined spatial location used for navigation"),
    ("UAV", "AUTONOMY", "autonomous flight",
     "flight conducted with limited or no direct human control"),
    ("UAV", "OBSTACLE_AVOID", "sense and avoid",
     "the capability to detect conflicts and take avoiding action"),
    ("UAV", "SWARM", "swarm",
     "a coordinated group of autonomous vehicles"),

    ("SYSTEMS", "REDUNDANCY", "redundancy",
     "the duplication of critical components or functions"),
    ("SYSTEMS", "FAULT_TOLERANCE", "fault tolerance",
     "the ability of a system to continue operating after certain failures"),
    ("SYSTEMS", "FMEA", "FMEA",
     "a structured method for identifying failure modes and their effects"),
    ("SYSTEMS", "RELIABILITY", "reliability",
     "the probability that a system performs its required function"),

    ("MAINT", "MAINTENANCE", "preventive maintenance",
     "scheduled maintenance intended to reduce the probability of failure"),
    ("MAINT", "NDT", "non-destructive testing",
     "inspection of a component without damaging it"),
    ("MAINT", "AIRWORTHINESS", "airworthiness directive",
     "a mandatory requirement issued to correct an unsafe condition"),
    ("MAINT", "MRO", "MRO",
     "maintenance, repair, and overhaul activities"),

    ("METHODS", "CFD", "computational fluid dynamics",
     "numerical simulation of fluid-flow governing equations"),
    ("METHODS", "FEM", "finite element method",
     "a numerical technique for solving discretized engineering field problems"),
    ("METHODS", "MONTE_CARLO", "Monte Carlo simulation",
     "analysis based on repeated random sampling"),
    ("METHODS", "SYSTEM_ID", "system identification",
     "estimating mathematical models from measured input-output data"),
]


class Command(BaseCommand):
    help = (
        "Create expanded AeroESP taxonomy and "
        "generate 100 deterministic demo questions."
    )

    def handle(self, *args, **options):

        domain_objects = {}
        topic_objects = {}

        # ---------------------------------------------
        # Taxonomy
        # ---------------------------------------------

        for domain_code, data in TAXONOMY.items():

            domain, _ = AerospaceDomain.objects.update_or_create(
                code=domain_code,
                defaults={
                    "name": data["name"],
                    "order": data["order"],
                    "is_active": True,
                },
            )

            domain_objects[domain_code] = domain

            for index, (topic_code, topic_name) in enumerate(
                data["topics"],
                start=1,
            ):

                topic, _ = AerospaceTopic.objects.update_or_create(
                    domain=domain,
                    code=topic_code,
                    defaults={
                        "name": topic_name,
                        "order": index,
                        "is_active": True,
                        "approval_status":
                            AerospaceTopic.ApprovalStatus.CORE,
                    },
                )

                topic_objects[
                    (domain_code, topic_code)
                ] = topic

        # ---------------------------------------------
        # 100 reproducible demo questions
        # ---------------------------------------------

        rng = random.Random(20260813)

        concepts_by_domain = {}

        for concept in CONCEPTS:
            concepts_by_domain.setdefault(
                concept[0],
                [],
            ).append(concept)

        created_or_updated = 0

        for index, concept in enumerate(CONCEPTS, start=1):

            (
                domain_code,
                topic_code,
                term,
                definition,
            ) = concept

            domain = domain_objects[domain_code]
            topic = topic_objects[
                (domain_code, topic_code)
            ]

            same_domain = [
                item
                for item in concepts_by_domain[domain_code]
                if item[2] != term
            ]

            distractors = rng.sample(
                same_domain,
                k=3,
            )

            # -----------------------------------------
            # Variant 1:
            # Definition -> Term
            # -----------------------------------------

            term_options = [
                term,
                distractors[0][2],
                distractors[1][2],
                distractors[2][2],
            ]

            rng.shuffle(term_options)

            correct_letter_1 = "ABCD"[
                term_options.index(term)
            ]

            ref1 = (
                f"DEMO100::{domain_code}::"
                f"{topic_code}::{term}::TERM"
            )

            Question.objects.update_or_create(
                source_reference=ref1,
                defaults={
                    "owner": None,
                    "question_text":
                        "Which aerospace term best matches "
                        f"the following definition?\n\n{definition}",
                    "option_a": term_options[0],
                    "option_b": term_options[1],
                    "option_c": term_options[2],
                    "option_d": term_options[3],
                    "correct_answer": correct_letter_1,
                    "explanation":
                        f"{term} means {definition}.",
                    "question_language":
                        Question.Language.ENGLISH,
                    "options_language":
                        Question.Language.ENGLISH,
                    "skill":
                        Question.Skill.VOCABULARY,
                    "domain_ref": domain,
                    "topic_ref": topic,
                    "aerospace_domain": domain_code,
                    "topic": topic.name,
                    "difficulty":
                        Question.Difficulty.BASIC
                        if index % 3 == 1
                        else (
                            Question.Difficulty.INTERMEDIATE
                            if index % 3 == 2
                            else Question.Difficulty.ADVANCED
                        ),
                    "source_type":
                        Question.SourceType.SEED,
                    "status":
                        Question.Status.DEMO,
                    "visibility":
                        Question.Visibility.PRACTICE_EXAM,
                    "version": 1,
                },
            )

            # -----------------------------------------
            # Variant 2:
            # Term -> Definition
            # -----------------------------------------

            definition_options = [
                definition,
                distractors[0][3],
                distractors[1][3],
                distractors[2][3],
            ]

            rng.shuffle(definition_options)

            correct_letter_2 = "ABCD"[
                definition_options.index(definition)
            ]

            ref2 = (
                f"DEMO100::{domain_code}::"
                f"{topic_code}::{term}::DEF"
            )

            Question.objects.update_or_create(
                source_reference=ref2,
                defaults={
                    "owner": None,
                    "question_text":
                        f"In aerospace engineering, what "
                        f"does the term '{term}' mean?",
                    "option_a": definition_options[0],
                    "option_b": definition_options[1],
                    "option_c": definition_options[2],
                    "option_d": definition_options[3],
                    "correct_answer": correct_letter_2,
                    "explanation":
                        f"{term} means {definition}.",
                    "question_language":
                        Question.Language.ENGLISH,
                    "options_language":
                        Question.Language.ENGLISH,
                    "skill":
                        Question.Skill.VOCABULARY,
                    "domain_ref": domain,
                    "topic_ref": topic,
                    "aerospace_domain": domain_code,
                    "topic": topic.name,
                    "difficulty":
                        Question.Difficulty.INTERMEDIATE,
                    "source_type":
                        Question.SourceType.SEED,
                    "status":
                        Question.Status.DEMO,
                    "visibility":
                        Question.Visibility.PRACTICE_EXAM,
                    "version": 1,
                },
            )

            created_or_updated += 2

        self.stdout.write(
            self.style.SUCCESS(
                "Expanded AeroESP taxonomy created. "
                f"Demo questions processed: {created_or_updated}"
            )
        )