from django.core.management.base import BaseCommand

from assessment.models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


TAXONOMY = [
    {
        "code": "AERO",
        "name": "Aerodynamics",
        "order": 1,
        "topics": [
            ("FUNDAMENTALS", "Aerodynamics Fundamentals"),
            ("BOUNDARY_LAYER", "Boundary Layer"),
            ("FLOW_SEPARATION", "Flow Separation"),
            ("COMPRESSIBLE", "Compressible Flow"),
            ("TURBULENCE", "Turbulence"),
            ("PERFORMANCE", "Aerodynamic Performance"),
            ("CFD", "Computational Fluid Dynamics"),
        ],
    },
    {
        "code": "FLIGHT",
        "name": "Flight Dynamics & Control",
        "order": 2,
        "topics": [
            ("AIRCRAFT_DYNAMICS", "Aircraft Dynamics"),
            ("STATIC_STABILITY", "Static Stability"),
            ("DYNAMIC_STABILITY", "Dynamic Stability"),
            ("FLIGHT_CONTROL", "Flight Control"),
            ("GUIDANCE", "Guidance"),
            ("NAVIGATION", "Navigation"),
            ("AUTOPILOT", "Autopilot"),
            ("AUTONOMOUS_FLIGHT", "UAV & Autonomous Flight"),
        ],
    },
    {
        "code": "PROP",
        "name": "Propulsion",
        "order": 3,
        "topics": [
            ("FUNDAMENTALS", "Propulsion Fundamentals"),
            ("GAS_TURBINE", "Gas Turbines"),
            ("JET_ENGINE", "Jet Engines"),
            ("ROCKET", "Rocket Propulsion"),
            ("PROPELLER", "Propeller Propulsion"),
            ("ELECTRIC", "Electric Propulsion"),
        ],
    },
    {
        "code": "STRUCT",
        "name": "Aerospace Structures",
        "order": 4,
        "topics": [
            ("STRUCTURAL_MECHANICS", "Structural Mechanics"),
            ("COMPOSITES", "Composite Structures"),
            ("AEROELASTICITY", "Aeroelasticity"),
            ("FATIGUE", "Fatigue & Failure"),
        ],
    },
    {
        "code": "SPACE",
        "name": "Space Engineering",
        "order": 5,
        "topics": [
            ("ORBITAL_MECHANICS", "Orbital Mechanics"),
            ("SPACECRAFT_DYNAMICS", "Spacecraft Dynamics"),
            (
                "ADCS",
                "Attitude Determination & Control",
            ),
            ("SPACE_PROPULSION", "Space Propulsion"),
        ],
    },
]


class Command(BaseCommand):
    help = "Create the initial AeroESP aerospace taxonomy."

    def handle(self, *args, **options):

        domain_map = {}

        for domain_data in TAXONOMY:

            domain, _ = AerospaceDomain.objects.update_or_create(
                code=domain_data["code"],
                defaults={
                    "name": domain_data["name"],
                    "order": domain_data["order"],
                    "is_active": True,
                },
            )

            domain_map[domain.code] = domain

            for index, (topic_code, topic_name) in enumerate(
                domain_data["topics"],
                start=1,
            ):
                AerospaceTopic.objects.update_or_create(
                    domain=domain,
                    code=topic_code,
                    defaults={
                        "name": topic_name,
                        "order": index,
                        "is_active": True,
                    },
                )

        # ---------------------------------------------
        # Backfill existing demo questions
        # ---------------------------------------------

        updated = 0

        for question in Question.objects.all():

            domain = domain_map.get(question.aerospace_domain)

            if domain:
                question.domain_ref = domain
                question.save(update_fields=[
                    "domain_ref",
                    "updated_at",
                ])
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Taxonomy created successfully. "
                f"Existing questions linked: {updated}"
            )
        )