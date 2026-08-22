from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from assessment.models import Question


class Command(BaseCommand):

    help = "Bootstrap extended Aerospace English question bank (all domains)"


    def handle(self, *args, **options):

        User = get_user_model()

        teacher = User.objects.get(
            username="habib"
        )

        questions = [

            # ==========================
            # GENERAL AEROSPACE
            # ==========================

            {
                "domain": "General Aerospace",
                "skill": "VOCAB",
                "level": "EASY",
                "text": "An aircraft that can take off and land vertically is called a:",
                "a": "airliner",
                "b": "VTOL aircraft",
                "c": "glider",
                "d": "trainer aircraft",
                "answer": "B",
            },

            {
                "domain": "General Aerospace",
                "skill": "VOCAB",
                "level": "EASY",
                "text": "The person responsible for flying an aircraft is the:",
                "a": "engineer",
                "b": "designer",
                "c": "pilot",
                "d": "technician",
                "answer": "C",
            },

            {
                "domain": "General Aerospace",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text": "The maximum weight of an aircraft allowed for operation is called:",
                "a": "empty weight",
                "b": "maximum takeoff weight",
                "c": "fuel weight",
                "d": "payload weight",
                "answer": "B",
            },

            {
                "domain": "General Aerospace",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text": "The primary purpose of an aircraft propulsion system is to:",
                "a": "generate thrust",
                "b": "reduce weight",
                "c": "increase drag",
                "d": "control temperature",
                "answer": "A",
            },

            {
                "domain": "General Aerospace",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text": "Payload refers to:",
                "a": "the aircraft structure",
                "b": "the useful carried load",
                "c": "engine temperature",
                "d": "fuel consumption",
                "answer": "B",
            },

            {
                "domain": "General Aerospace",
                "skill": "GRAMMAR",
                "level": "MEDIUM",
                "text": "The aircraft ______ tested before the first flight.",
                "a": "was",
                "b": "were",
                "c": "are",
                "d": "have",
                "answer": "A",
            },

            {
                "domain": "General Aerospace",
                "skill": "READING",
                "level": "MEDIUM",
                "text":
                "Aircraft maintenance is necessary to ensure safety and reliability. "
                "What is the main purpose of maintenance?",
                "a": "Increase noise",
                "b": "Improve safety",
                "c": "Reduce passengers",
                "d": "Change weather",
                "answer": "B",
            },


            # ==========================
            # AERODYNAMICS
            # ==========================

            {
                "domain": "Aerodynamics",
                "skill": "VOCAB",
                "level": "EASY",
                "text": "The force that supports an aircraft in flight is called:",
                "a": "drag",
                "b": "lift",
                "c": "weight",
                "d": "thrust",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "VOCAB",
                "level": "EASY",
                "text": "The force opposing aircraft motion through air is:",
                "a": "lift",
                "b": "weight",
                "c": "drag",
                "d": "moment",
                "answer": "C",
            },

            {
                "domain": "Aerodynamics",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Increasing angle of attack generally increases lift until:",
                "a": "engine failure",
                "b": "stall occurs",
                "c": "fuel decreases",
                "d": "drag disappears",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The thin region close to a surface affected by viscosity is called:",
                "a": "shock wave",
                "b": "boundary layer",
                "c": "wake",
                "d": "streamline",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A stall happens when:",
                "a": "lift decreases after critical angle of attack",
                "b": "fuel tank is empty",
                "c": "engine stops",
                "d": "drag becomes zero",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The shape of an aircraft wing cross section is called:",
                "a": "airfoil",
                "b": "fuselage",
                "c": "propeller",
                "d": "nozzle",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The Reynolds number represents the relationship between:",
                "a": "gravity and weight",
                "b": "inertial and viscous forces",
                "c": "temperature and pressure",
                "d": "fuel and thrust",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Flow separation occurs when:",
                "a": "air follows the surface perfectly",
                "b": "boundary layer leaves the surface",
                "c": "velocity becomes constant",
                "d": "pressure becomes zero",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A higher aspect ratio wing usually produces:",
                "a": "higher induced drag",
                "b": "lower induced drag",
                "c": "zero lift",
                "d": "higher weight only",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Mach number is the ratio between aircraft velocity and:",
                "a": "air density",
                "b": "speed of sound",
                "c": "wing length",
                "d": "gravity",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The coefficient of lift mainly depends on:",
                "a": "aircraft color",
                "b": "angle of attack and airfoil shape",
                "c": "pilot age",
                "d": "fuel type",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The region behind an aircraft where disturbed airflow exists is called:",
                "a": "wake",
                "b": "cockpit",
                "c": "cabin",
                "d": "engine bay",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Induced drag is mainly associated with:",
                "a": "lift generation",
                "b": "engine operation",
                "c": "aircraft weight only",
                "d": "fuel temperature",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The point where aerodynamic forces are considered to act is called:",
                "a": "center of gravity",
                "b": "center of pressure",
                "c": "fuel center",
                "d": "rotation point",
                "answer": "B",
            },

            {
                "domain": "Aerodynamics",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Increasing air velocity generally causes dynamic pressure to:",
                "a": "increase",
                "b": "decrease",
                "c": "become zero",
                "d": "remain constant",
                "answer": "A",
            },


            # ==========================
            # FLIGHT DYNAMICS & CONTROL
            # ==========================

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Rotation around the longitudinal axis is called:",
                "a": "pitch",
                "b": "yaw",
                "c": "roll",
                "d": "heave",
                "answer": "C",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Rotation around the lateral axis is called:",
                "a": "pitch",
                "b": "roll",
                "c": "yaw",
                "d": "slide",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Rotation around the vertical axis is called:",
                "a": "pitch",
                "b": "roll",
                "c": "yaw",
                "d": "lift",
                "answer": "C",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The elevator is mainly used to control:",
                "a": "pitch motion",
                "b": "engine speed",
                "c": "fuel flow",
                "d": "landing gear",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The ailerons are mainly used for controlling:",
                "a": "yaw",
                "b": "roll",
                "c": "pitch",
                "d": "thrust",
                "answer": "B",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The rudder controls aircraft motion in:",
                "a": "yaw direction",
                "b": "vertical acceleration only",
                "c": "engine rotation",
                "d": "fuel pressure",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "An aircraft that returns to its original position after disturbance is:",
                "a": "unstable",
                "b": "stable",
                "c": "damaged",
                "d": "overloaded",
                "answer": "B",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Static stability describes the aircraft's initial response to:",
                "a": "a disturbance",
                "b": "fuel consumption",
                "c": "engine failure",
                "d": "landing speed",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Dynamic stability is related to:",
                "a": "motion response with time",
                "b": "aircraft color",
                "c": "fuel capacity",
                "d": "structural material",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "An autopilot system is designed to:",
                "a": "automatically control aircraft attitude",
                "b": "produce fuel",
                "c": "increase weight",
                "d": "replace wings",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The center of gravity location affects:",
                "a": "aircraft stability",
                "b": "paint quality",
                "c": "engine noise",
                "d": "radio frequency",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A sensor used to measure angular rate is called:",
                "a": "gyroscope",
                "b": "thermometer",
                "c": "fuel gauge",
                "d": "altimeter",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The instrument that measures altitude is:",
                "a": "airspeed indicator",
                "b": "altimeter",
                "c": "gyroscope",
                "d": "compass",
                "answer": "B",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Feedback control systems use output information to:",
                "a": "improve control performance",
                "b": "increase aircraft weight",
                "c": "remove sensors",
                "d": "stop communication",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Longitudinal stability mainly involves motion in the:",
                "a": "pitch axis",
                "b": "roll axis",
                "c": "yaw axis",
                "d": "engine axis",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Directional stability is related to motion around the:",
                "a": "pitch axis",
                "b": "yaw axis",
                "c": "roll axis",
                "d": "vertical acceleration axis",
                "answer": "B",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The system that determines aircraft position using satellites is:",
                "a": "GPS",
                "b": "radar",
                "c": "engine control",
                "d": "hydraulic system",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "An increase in control surface deflection usually causes:",
                "a": "greater aerodynamic moment",
                "b": "zero lift",
                "c": "engine shutdown",
                "d": "fuel reduction",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The device that measures aircraft acceleration is called:",
                "a": "accelerometer",
                "b": "altimeter",
                "c": "tachometer",
                "d": "barometer",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A fly-by-wire system replaces traditional mechanical controls with:",
                "a": "electronic signals",
                "b": "larger wings",
                "c": "extra fuel tanks",
                "d": "manual cables only",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics & Control",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The commanded orientation of an aircraft is called:",
                "a": "attitude",
                "b": "payload",
                "c": "thrust",
                "d": "density",
                "answer": "A",
            },


            # ==========================
            # PROPULSION
            # ==========================

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The force produced by an aircraft engine is called:",
                "a": "lift",
                "b": "drag",
                "c": "thrust",
                "d": "weight",
                "answer": "C",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A gas turbine engine produces thrust by:",
                "a": "accelerating exhaust gases",
                "b": "reducing air pressure",
                "c": "stopping airflow",
                "d": "increasing aircraft weight",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The component that increases air pressure in a jet engine is:",
                "a": "turbine",
                "b": "compressor",
                "c": "nozzle",
                "d": "fan only",
                "answer": "B",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The main purpose of the combustion chamber is to:",
                "a": "burn fuel and release energy",
                "b": "compress air",
                "c": "reduce velocity",
                "d": "control landing",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The hot gases leaving a turbine engine pass through the:",
                "a": "nozzle",
                "b": "cockpit",
                "c": "wing",
                "d": "landing gear",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A turbofan engine is widely used in commercial aircraft because of:",
                "a": "high efficiency and lower noise",
                "b": "zero fuel consumption",
                "c": "no moving parts",
                "d": "very low temperature operation",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The ratio between useful output power and input power is called:",
                "a": "efficiency",
                "b": "pressure",
                "c": "velocity",
                "d": "density",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The turbine in a gas turbine engine extracts energy from:",
                "a": "hot gases",
                "b": "fuel tanks",
                "c": "aircraft wings",
                "d": "landing systems",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Fuel consumption of an aircraft engine is usually measured as:",
                "a": "specific fuel consumption",
                "b": "lift coefficient",
                "c": "Mach angle",
                "d": "wing loading",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Increasing compressor pressure ratio generally improves:",
                "a": "engine efficiency",
                "b": "aircraft color",
                "c": "landing speed",
                "d": "structural flexibility",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A rocket engine differs from a jet engine because it:",
                "a": "carries its oxidizer",
                "b": "requires atmospheric oxygen",
                "c": "has no combustion",
                "d": "cannot produce thrust",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A propeller converts engine power into:",
                "a": "thrust",
                "b": "drag only",
                "c": "weight",
                "d": "temperature",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The rotating component that extracts energy from exhaust gases is:",
                "a": "compressor",
                "b": "turbine",
                "c": "nozzle",
                "d": "diffuser",
                "answer": "B",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Afterburners increase thrust by:",
                "a": "burning additional fuel in exhaust flow",
                "b": "reducing engine temperature",
                "c": "stopping airflow",
                "d": "decreasing pressure",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The ratio of mass flow rate to engine size is related to:",
                "a": "engine performance",
                "b": "aircraft color",
                "c": "wing shape only",
                "d": "landing gear",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A diffuser in an engine is used to:",
                "a": "reduce velocity and increase pressure",
                "b": "increase aircraft weight",
                "c": "produce fuel",
                "d": "control landing",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "A device that mixes fuel and air before combustion is:",
                "a": "injector",
                "b": "wing",
                "c": "elevator",
                "d": "sensor",
                "answer": "A",
            },

            {
                "domain": "Propulsion",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Engine thrust generally increases when:",
                "a": "mass flow and exhaust velocity increase",
                "b": "airflow stops",
                "c": "fuel is removed",
                "d": "temperature becomes zero",
                "answer": "A",
            },


            # ==========================
            # STRUCTURES
            # ==========================

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The ability of a structure to resist applied forces is called:",
                "a": "strength",
                "b": "velocity",
                "c": "thrust",
                "d": "lift",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The deformation of a material under load is called:",
                "a": "strain",
                "b": "stress",
                "c": "fatigue",
                "d": "density",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The internal force per unit area in a material is:",
                "a": "stress",
                "b": "strain",
                "c": "weight",
                "d": "moment",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Fatigue failure is mainly caused by:",
                "a": "repeated loading cycles",
                "b": "single temperature change",
                "c": "low speed only",
                "d": "fuel consumption",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Materials made from two or more combined materials are:",
                "a": "composites",
                "b": "metals only",
                "c": "fluids",
                "d": "ceramics only",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Aluminum is widely used in aircraft structures because of:",
                "a": "high strength-to-weight ratio",
                "b": "very high density",
                "c": "low durability",
                "d": "poor strength",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A force that tends to stretch a material is:",
                "a": "tension",
                "b": "compression",
                "c": "torsion",
                "d": "shear",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A force that pushes a material together is:",
                "a": "compression",
                "b": "tension",
                "c": "bending",
                "d": "torsion",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The main advantage of composite materials in aircraft is:",
                "a": "low weight and high strength",
                "b": "high corrosion only",
                "c": "low temperature",
                "d": "zero maintenance",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The force that causes twisting deformation is:",
                "a": "torsion",
                "b": "compression",
                "c": "pressure",
                "d": "lift",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A safety factor is used in design to:",
                "a": "provide additional strength margin",
                "b": "reduce aircraft size only",
                "c": "increase noise",
                "d": "remove testing",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The ability of a material to return to original shape is:",
                "a": "elasticity",
                "b": "plasticity",
                "c": "fatigue",
                "d": "fracture",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Buckling is a failure mode commonly associated with:",
                "a": "compression loads",
                "b": "fuel pressure",
                "c": "temperature only",
                "d": "aerodynamic lift",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The main purpose of structural analysis is to determine:",
                "a": "stress and deformation",
                "b": "fuel quantity",
                "c": "engine speed",
                "d": "aircraft color",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A crack that grows due to repeated loading is related to:",
                "a": "fatigue",
                "b": "lift",
                "c": "thrust",
                "d": "drag",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Finite element analysis is commonly used for:",
                "a": "structural simulation",
                "b": "fuel production",
                "c": "navigation",
                "d": "weather prediction",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The ability of a material to absorb energy before failure is:",
                "a": "toughness",
                "b": "density",
                "c": "velocity",
                "d": "pressure",
                "answer": "A",
            },

            {
                "domain": "Structures",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A lighter aircraft structure can improve:",
                "a": "fuel efficiency",
                "b": "drag only",
                "c": "engine temperature",
                "d": "noise only",
                "answer": "A",
            },


            # ==========================
            # SPACE & SATELLITE
            # ==========================

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "A spacecraft placed into orbit around Earth is called:",
                "a": "satellite",
                "b": "airfoil",
                "c": "engine",
                "d": "glider",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The path followed by a satellite around a planet is called:",
                "a": "orbit",
                "b": "trajectory only",
                "c": "runway",
                "d": "airway",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A satellite remains in orbit because of the balance between:",
                "a": "gravity and orbital velocity",
                "b": "fuel and temperature",
                "c": "pressure and density",
                "d": "weight and lift",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The system responsible for controlling spacecraft orientation is:",
                "a": "attitude control system",
                "b": "fuel system",
                "c": "landing system",
                "d": "propeller system",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A communication satellite is mainly used for:",
                "a": "transmitting signals",
                "b": "producing aircraft thrust",
                "c": "measuring wing stress",
                "d": "controlling engines",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The energy source commonly used by satellites is:",
                "a": "solar panels",
                "b": "jet fuel",
                "c": "gas turbine",
                "d": "propeller",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Low Earth Orbit satellites usually operate:",
                "a": "close to Earth",
                "b": "near the Sun",
                "c": "inside atmosphere only",
                "d": "without gravity",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A system used to determine spacecraft position is:",
                "a": "navigation system",
                "b": "combustion system",
                "c": "hydraulic system",
                "d": "cooling system",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The main function of a satellite payload is:",
                "a": "performing the mission task",
                "b": "providing structure only",
                "c": "producing fuel",
                "d": "cooling the spacecraft",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A rocket used to place spacecraft into orbit is called:",
                "a": "launch vehicle",
                "b": "airliner",
                "c": "glider",
                "d": "trainer aircraft",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Escape velocity is the minimum velocity required to:",
                "a": "leave a gravitational field",
                "b": "increase aircraft lift",
                "c": "reduce drag",
                "d": "start an engine",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Telemetry is the process of:",
                "a": "sending measurement data",
                "b": "producing thrust",
                "c": "controlling wings",
                "d": "repairing structures",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A satellite requires thermal control because:",
                "a": "space has extreme temperatures",
                "b": "gravity disappears",
                "c": "fuel freezes always",
                "d": "orbit stops",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A geostationary satellite has an orbital period equal to:",
                "a": "Earth rotation period",
                "b": "one hour",
                "c": "one day only by chance",
                "d": "zero",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The subsystem responsible for electrical power generation is:",
                "a": "Electrical Power System",
                "b": "Propulsion System",
                "c": "Thermal System",
                "d": "Payload System",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Increasing satellite altitude generally results in:",
                "a": "longer orbital period",
                "b": "higher atmospheric drag",
                "c": "lower communication range",
                "d": "loss of gravity",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A spacecraft's ability to maintain its orientation is called:",
                "a": "attitude stability",
                "b": "fuel efficiency",
                "c": "aerodynamic lift",
                "d": "structural strength",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Space debris is dangerous because it can:",
                "a": "damage spacecraft during collision",
                "b": "increase satellite power",
                "c": "reduce gravity",
                "d": "stop Earth rotation",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A small spacecraft designed for scientific missions is called:",
                "a": "space probe",
                "b": "airliner",
                "c": "helicopter",
                "d": "glider",
                "answer": "A",
            },

            {
                "domain": "Space & Satellite",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The main advantage of reusable launch vehicles is:",
                "a": "reduced launch cost",
                "b": "higher aircraft speed",
                "c": "lower gravity",
                "d": "elimination of propulsion",
                "answer": "A",
            },


            # ==========================
            # UAV
            # ==========================

            {
                "domain": "UAV",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "UAV stands for:",
                "a": "Unmanned Aerial Vehicle",
                "b": "Universal Aviation Vehicle",
                "c": "United Aircraft Version",
                "d": "Ultra Air Velocity",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "CONCEPT",
                "level": "EASY",
                "text":
                "A UAV can operate without:",
                "a": "a human pilot onboard",
                "b": "a control system",
                "c": "a power source",
                "d": "a communication system",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The system that controls UAV movement is called:",
                "a": "flight controller",
                "b": "fuel tank",
                "c": "landing gear",
                "d": "payload",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "An autopilot system allows a UAV to:",
                "a": "fly automatically",
                "b": "increase fuel density",
                "c": "change material properties",
                "d": "remove aerodynamic forces",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The useful equipment carried by a UAV is called:",
                "a": "payload",
                "b": "fuselage",
                "c": "winglet",
                "d": "actuator",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A major advantage of UAVs is:",
                "a": "performing dangerous missions without risking pilots",
                "b": "eliminating all maintenance",
                "c": "requiring no energy",
                "d": "having unlimited range",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The communication link between operator and UAV is called:",
                "a": "data link",
                "b": "wing link",
                "c": "engine link",
                "d": "fuel link",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "GPS is commonly used in UAVs for:",
                "a": "position estimation and navigation",
                "b": "engine combustion",
                "c": "structural analysis",
                "d": "wing design",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A sensor used to measure aircraft acceleration is:",
                "a": "accelerometer",
                "b": "altimeter only",
                "c": "fuel sensor",
                "d": "temperature sensor",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Obstacle avoidance systems mainly improve:",
                "a": "flight safety",
                "b": "engine power",
                "c": "material strength",
                "d": "fuel production",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A drone with multiple rotors is commonly called:",
                "a": "multirotor UAV",
                "b": "jet aircraft",
                "c": "glider",
                "d": "satellite",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The flight endurance of a UAV refers to:",
                "a": "maximum time it can remain airborne",
                "b": "maximum structural stress",
                "c": "engine temperature",
                "d": "wing thickness",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A system that collects information from the environment is called:",
                "a": "sensor system",
                "b": "fuel system",
                "c": "landing system",
                "d": "propulsion system",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The main purpose of a UAV ground control station is:",
                "a": "monitoring and controlling the UAV mission",
                "b": "producing aircraft fuel",
                "c": "repairing wings",
                "d": "generating lift",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The vertical distance of a UAV above ground is called:",
                "a": "altitude",
                "b": "velocity",
                "c": "acceleration",
                "d": "pressure",
                "answer": "A",
            },

            {
                "domain": "UAV",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Autonomous UAV navigation requires:",
                "a": "sensors, algorithms, and control systems",
                "b": "only fuel",
                "c": "only wings",
                "d": "only communication",
                "answer": "A",
            },


            # ==========================
            # AIRCRAFT SYSTEMS
            # ==========================

            {
                "domain": "Aircraft Systems",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The system responsible for supplying electrical power is:",
                "a": "electrical system",
                "b": "fuel system",
                "c": "landing system",
                "d": "navigation system",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The hydraulic system in aircraft is mainly used for:",
                "a": "powering actuators",
                "b": "producing fuel",
                "c": "measuring altitude",
                "d": "communication",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The device that converts electrical signals into mechanical movement is:",
                "a": "actuator",
                "b": "sensor",
                "c": "antenna",
                "d": "battery",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The avionics system includes:",
                "a": "electronic aircraft systems",
                "b": "only engines",
                "c": "only structures",
                "d": "only landing gear",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The system used to measure aircraft altitude is:",
                "a": "altimeter",
                "b": "accelerometer",
                "c": "thermometer",
                "d": "tachometer",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The purpose of a flight control system is:",
                "a": "control aircraft motion",
                "b": "increase fuel quantity",
                "c": "reduce passenger weight",
                "d": "produce electricity",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A device that detects physical conditions is called:",
                "a": "sensor",
                "b": "actuator",
                "c": "controller",
                "d": "transmitter",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Fly-by-wire systems replace traditional mechanical controls with:",
                "a": "electronic signals",
                "b": "hydraulic pipes only",
                "c": "cables only",
                "d": "manual force only",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The system responsible for aircraft temperature control is:",
                "a": "environmental control system",
                "b": "fuel system",
                "c": "navigation system",
                "d": "propulsion system",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Redundancy in aircraft systems improves:",
                "a": "reliability and safety",
                "b": "fuel consumption only",
                "c": "aircraft weight only",
                "d": "engine noise",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The landing gear system is used during:",
                "a": "takeoff and landing",
                "b": "engine combustion",
                "c": "cruise only",
                "d": "communication",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The purpose of an anti-icing system is:",
                "a": "prevent ice formation",
                "b": "increase aircraft weight",
                "c": "reduce engine power",
                "d": "stop navigation",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The primary function of the fuel system is to:",
                "a": "store and supply fuel to engines",
                "b": "control aircraft attitude",
                "c": "measure altitude",
                "d": "generate lift",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The system that provides information about aircraft position is:",
                "a": "navigation system",
                "b": "hydraulic system",
                "c": "fuel system",
                "d": "cooling system",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "An aircraft data recorder is mainly used for:",
                "a": "recording flight information",
                "b": "controlling engines",
                "c": "increasing speed",
                "d": "reducing weight",
                "answer": "A",
            },

            {
                "domain": "Aircraft Systems",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The cockpit display system provides:",
                "a": "flight information to pilots",
                "b": "fuel production",
                "c": "structural repair",
                "d": "engine manufacturing",
                "answer": "A",
            },


            # ==========================
            # AVIATION SAFETY
            # ==========================

            {
                "domain": "Aviation Safety",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "A condition that may cause an accident is called:",
                "a": "hazard",
                "b": "payload",
                "c": "altitude",
                "d": "velocity",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The main goal of aviation safety management is:",
                "a": "preventing accidents and reducing risks",
                "b": "increasing aircraft weight",
                "c": "reducing passenger comfort",
                "d": "eliminating maintenance",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A process used to identify and evaluate risks is called:",
                "a": "risk assessment",
                "b": "flight control",
                "c": "propulsion analysis",
                "d": "navigation",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Human factors in aviation mainly study:",
                "a": "interaction between humans and systems",
                "b": "engine design only",
                "c": "aircraft color",
                "d": "fuel chemistry",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "An unwanted event that causes damage is an:",
                "a": "accident",
                "b": "orbit",
                "c": "operation",
                "d": "inspection",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "An event that could have caused an accident but did not is called:",
                "a": "incident",
                "b": "mission",
                "c": "takeoff",
                "d": "maneuver",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Safety Management System (SMS) is designed to:",
                "a": "manage safety risks systematically",
                "b": "increase aircraft speed",
                "c": "replace pilots",
                "d": "remove regulations",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A detailed examination of aircraft condition is called:",
                "a": "inspection",
                "b": "navigation",
                "c": "simulation",
                "d": "communication",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Checklists are important because they:",
                "a": "reduce human errors",
                "b": "increase aircraft weight",
                "c": "replace maintenance",
                "d": "control weather",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Emergency procedures are developed to:",
                "a": "handle abnormal situations",
                "b": "increase fuel consumption",
                "c": "change aircraft design",
                "d": "reduce communication",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The purpose of accident investigation is mainly to:",
                "a": "prevent future accidents",
                "b": "assign blame only",
                "c": "increase ticket prices",
                "d": "stop aviation operations",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Aviation regulations are created to:",
                "a": "ensure safe operations",
                "b": "increase aircraft noise",
                "c": "reduce technology",
                "d": "limit training",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Crew Resource Management (CRM) focuses on:",
                "a": "teamwork and communication",
                "b": "engine design",
                "c": "fuel production",
                "d": "structural analysis",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The concept of safety culture refers to:",
                "a": "shared attitudes and practices toward safety",
                "b": "aircraft speed improvement",
                "c": "engine manufacturing",
                "d": "fuel management",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The probability and consequence of a hazard are used to evaluate:",
                "a": "risk",
                "b": "altitude",
                "c": "velocity",
                "d": "thrust",
                "answer": "A",
            },

            {
                "domain": "Aviation Safety",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A proactive safety approach attempts to:",
                "a": "identify risks before accidents occur",
                "b": "wait for accidents",
                "c": "remove all procedures",
                "d": "ignore human factors",
                "answer": "A",
            },


            # ==========================
            # AIRCRAFT MAINTENANCE
            # ==========================

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Maintenance is the process of:",
                "a": "keeping aircraft safe and operational",
                "b": "increasing aircraft weight",
                "c": "changing weather conditions",
                "d": "designing airports",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Scheduled maintenance is performed:",
                "a": "according to planned intervals",
                "b": "only after accidents",
                "c": "without procedures",
                "d": "only during flight",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The main purpose of preventive maintenance is:",
                "a": "avoiding failures before they occur",
                "b": "increasing aircraft speed",
                "c": "changing aircraft structure",
                "d": "reducing training",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A person responsible for inspecting and repairing aircraft is:",
                "a": "maintenance technician",
                "b": "passenger",
                "c": "dispatcher",
                "d": "navigator",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Reliability analysis is used to study:",
                "a": "failure behavior of systems",
                "b": "aircraft color",
                "c": "airport location",
                "d": "passenger service",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A component failure that occurs unexpectedly is called:",
                "a": "random failure",
                "b": "scheduled maintenance",
                "c": "normal operation",
                "d": "inspection",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A maintenance manual provides:",
                "a": "technical instructions for maintenance tasks",
                "b": "weather forecasts",
                "c": "passenger information",
                "d": "airport maps",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The abbreviation MEL means:",
                "a": "Minimum Equipment List",
                "b": "Maximum Engine Level",
                "c": "Main Electrical Line",
                "d": "Mechanical Energy Load",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Condition-based maintenance depends mainly on:",
                "a": "monitoring equipment condition",
                "b": "fixed time only",
                "c": "pilot preference",
                "d": "weather conditions",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A tool used to find hidden defects inside materials is:",
                "a": "non-destructive testing",
                "b": "flight testing",
                "c": "navigation",
                "d": "simulation only",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The purpose of inspection is to:",
                "a": "detect problems and ensure safety",
                "b": "increase aircraft speed",
                "c": "reduce communication",
                "d": "replace design",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A maintenance action performed after failure is:",
                "a": "corrective maintenance",
                "b": "preventive maintenance",
                "c": "scheduled flight",
                "d": "navigation",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Reliability-centered maintenance focuses on:",
                "a": "maintaining critical functions effectively",
                "b": "reducing all inspections",
                "c": "removing safety procedures",
                "d": "increasing aircraft mass",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "AMM stands for:",
                "a": "Aircraft Maintenance Manual",
                "b": "Aircraft Motion Measurement",
                "c": "Automatic Mission Mode",
                "d": "Airplane Management Model",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The Aircraft Maintenance Manual provides:",
                "a": "procedures for aircraft maintenance tasks",
                "b": "passenger information",
                "c": "weather reports",
                "d": "airport schedules",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "SRM stands for:",
                "a": "Structural Repair Manual",
                "b": "System Reliability Model",
                "c": "Safety Regulation Manual",
                "d": "Service Route Map",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The Structural Repair Manual is mainly used for:",
                "a": "repairing aircraft structures",
                "b": "controlling engines",
                "c": "navigation planning",
                "d": "flight scheduling",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "IPC in aircraft documentation means:",
                "a": "Illustrated Parts Catalog",
                "b": "Internal Power Control",
                "c": "Integrated Pilot Computer",
                "d": "Inspection Planning Code",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The Illustrated Parts Catalog helps technicians to:",
                "a": "identify aircraft parts",
                "b": "control flight attitude",
                "c": "calculate lift",
                "d": "operate engines",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "MEL allows an aircraft to operate with:",
                "a": "certain inoperative equipment under conditions",
                "b": "no maintenance",
                "c": "no pilot",
                "d": "unlimited failures",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A maintenance record is important because it:",
                "a": "documents performed maintenance actions",
                "b": "controls weather",
                "c": "changes aircraft design",
                "d": "replaces inspection",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A defect means:",
                "a": "a fault or abnormal condition",
                "b": "a normal operation",
                "c": "a flight route",
                "d": "a fuel type",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Troubleshooting is the process of:",
                "a": "finding and correcting faults",
                "b": "increasing aircraft speed",
                "c": "designing airports",
                "d": "training passengers",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A component that can be removed and replaced is called:",
                "a": "replaceable unit",
                "b": "fixed structure",
                "c": "payload",
                "d": "orbit",
                "answer": "A",
            },

            {
                "domain": "Aircraft Maintenance",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Maintenance planning aims to:",
                "a": "schedule tasks efficiently and safely",
                "b": "increase aircraft weight",
                "c": "remove regulations",
                "d": "avoid documentation",
                "answer": "A",
            },


            # ==========================
            # TECHNICAL AEROSPACE ENGLISH
            # ==========================

            {
                "domain": "Technical Aerospace English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'inspect' means:",
                "a": "to examine carefully",
                "b": "to destroy",
                "c": "to replace completely",
                "d": "to accelerate",
                "answer": "A",
            },

            {
                "domain": "Technical Aerospace English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'decrease' means:",
                "a": "become smaller",
                "b": "increase rapidly",
                "c": "remain unchanged",
                "d": "rotate",
                "answer": "A",
            },

            {
                "domain": "Technical Aerospace English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'failure' in engineering refers to:",
                "a": "loss of required function",
                "b": "successful operation",
                "c": "high performance",
                "d": "normal condition",
                "answer": "A",
            },

            {
                "domain": "Technical Aerospace English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'requirement' means:",
                "a": "a necessary condition",
                "b": "a random event",
                "c": "a failure mode",
                "d": "a measurement error",
                "answer": "A",
            },

            {
                "domain": "Technical Aerospace English",
                "skill": "READING",
                "level": "HARD",
                "text":
                "Aircraft manufacturers publish technical manuals mainly to:",
                "a": "provide standardized maintenance information",
                "b": "advertise aircraft",
                "c": "replace pilots",
                "d": "reduce training",
                "answer": "A",
            },


            # ==========================
            # TECHNICAL READING
            # ==========================

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "MEDIUM",
                "text":
                """
Jet engines produce thrust by accelerating air and combustion gases.
The engine compresses incoming air, mixes it with fuel, and burns the mixture
inside the combustion chamber. The hot gases expand and leave the engine at
high velocity, creating thrust.

Question:
What is the main purpose of the combustion chamber?
                """,
                "a": "To burn the fuel-air mixture",
                "b": "To cool the aircraft",
                "c": "To control navigation",
                "d": "To store fuel",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "MEDIUM",
                "text":
                """
Jet engines produce thrust by accelerating air and combustion gases.
The engine compresses incoming air, mixes it with fuel, and burns the mixture
inside the combustion chamber. The hot gases expand and leave the engine at
high velocity, creating thrust.

Question:
According to the passage, thrust is produced mainly because:
                """,
                "a": "gas exits at high velocity",
                "b": "fuel is stored in the wing",
                "c": "the aircraft becomes heavier",
                "d": "the temperature decreases",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
The boundary layer is a thin region of airflow near an aerodynamic surface.
The characteristics of this layer strongly affect drag and flow separation.
Engineers study boundary layer behavior to improve aerodynamic performance.

Question:
Why do engineers study the boundary layer?
                """,
                "a": "To improve aerodynamic performance",
                "b": "To increase aircraft weight",
                "c": "To produce fuel",
                "d": "To control satellites",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "MEDIUM",
                "text":
                """
The flight control system allows pilots to control aircraft motion.
Modern aircraft often use fly-by-wire technology, where electronic signals
replace traditional mechanical connections between controls and actuators.

Question:
What replaces mechanical connections in fly-by-wire systems?
                """,
                "a": "Electronic signals",
                "b": "Fuel pressure",
                "c": "Engine thrust",
                "d": "Hydraulic fluid only",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Satellite communication systems transmit information between Earth stations
and satellites. These systems require antennas, power systems, and reliable
communication links to operate effectively.

Question:
What is required for reliable satellite communication?
                """,
                "a": "Communication links and supporting systems",
                "b": "Aircraft engines",
                "c": "Landing gear",
                "d": "Wing structures",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "MEDIUM",
                "text":
                """
Aircraft structures are designed to withstand different types of loads during
flight. Engineers analyze stress, deformation, and fatigue to ensure structural
safety.

Question:
What factors are analyzed in structural design?
                """,
                "a": "Stress, deformation, and fatigue",
                "b": "Passenger preferences",
                "c": "Fuel price",
                "d": "Weather forecast",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "MEDIUM",
                "text":
                """
Unmanned aerial vehicles use sensors, communication systems, and controllers
to perform missions without a pilot onboard. Autonomous operation requires
accurate navigation and reliable decision-making systems.

Question:
Which systems are important for UAV autonomous operation?
                """,
                "a": "Sensors, communication, and controllers",
                "b": "Only fuel tanks",
                "c": "Only wings",
                "d": "Only landing gear",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Aircraft maintenance manuals contain detailed instructions for inspection,
repair, and replacement procedures. Technicians use these documents to ensure
that maintenance tasks are performed according to approved standards.

Question:
Why do technicians use maintenance manuals?
                """,
                "a": "To perform approved maintenance procedures",
                "b": "To design airports",
                "c": "To control weather",
                "d": "To increase passenger numbers",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Battery health is an important factor in electric aircraft operation.
Degradation can reduce available energy and power capability. Battery
management systems monitor voltage, current, temperature, and state of health.

Question:
What parameters are monitored by battery management systems?
                """,
                "a": "Voltage, current, temperature, and state of health",
                "b": "Aircraft color and shape",
                "c": "Passenger weight only",
                "d": "Wing geometry only",
                "answer": "A",
            },

            {
                "domain": "Technical Reading",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Electric vertical takeoff and landing aircraft require efficient energy
management because battery capacity directly affects mission capability.
Engineers evaluate energy consumption, remaining power margin, and operational
limits.

Question:
Why is energy management important for eVTOL aircraft?
                """,
                "a": "Because battery capability affects mission feasibility",
                "b": "Because aircraft do not need batteries",
                "c": "Because gravity disappears",
                "d": "Because engines are unnecessary",
                "answer": "A",
            },


            # ==========================
            # AEROSPACE ACADEMIC WRITING
            # ==========================

            {
                "domain": "Academic Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'evaluate' in a research paper means:",
                "a": "to assess or analyze",
                "b": "to remove completely",
                "c": "to ignore results",
                "d": "to manufacture",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The purpose of an abstract in a scientific paper is to:",
                "a": "summarize the main research",
                "b": "describe only references",
                "c": "replace all figures",
                "d": "provide experimental equipment",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'methodology' refers to:",
                "a": "the methods used in research",
                "b": "the final conclusion only",
                "c": "the title of a paper",
                "d": "the author's biography",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "A conclusion section in a research paper usually:",
                "a": "summarizes findings and implications",
                "b": "introduces unrelated topics",
                "c": "lists only equations",
                "d": "describes laboratory equipment only",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'significant' in engineering papers usually means:",
                "a": "important or meaningful",
                "b": "incorrect",
                "c": "temporary",
                "d": "unknown",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The phrase 'the results indicate that' means:",
                "a": "the results suggest or show",
                "b": "the results are deleted",
                "c": "the experiment failed completely",
                "d": "the data is unavailable",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A literature review is used to:",
                "a": "discuss previous studies related to a topic",
                "b": "replace experimental results",
                "c": "describe only software",
                "d": "remove citations",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'parameter' refers to:",
                "a": "a measurable variable in a system",
                "b": "a passenger",
                "c": "a maintenance manual",
                "d": "a component failure",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A figure in a technical paper is mainly used to:",
                "a": "present visual information",
                "b": "replace the abstract",
                "c": "remove explanations",
                "d": "increase paper length",
                "answer": "A",
            },

            {
                "domain": "Academic Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'investigate' means:",
                "a": "to study carefully",
                "b": "to ignore",
                "c": "to simplify completely",
                "d": "to destroy",
                "answer": "A",
            },


            # ==========================
            # AEROSPACE GRAMMAR
            # ==========================

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "MEDIUM",
                "text":
                "The aircraft _____ tested under different conditions.",
                "a": "was",
                "b": "were",
                "c": "are",
                "d": "have",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "MEDIUM",
                "text":
                "Engine performance _____ affected by temperature.",
                "a": "is",
                "b": "are",
                "c": "were",
                "d": "have",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "MEDIUM",
                "text":
                "The experiment was conducted _____ evaluate aerodynamic behavior.",
                "a": "to",
                "b": "for",
                "c": "at",
                "d": "with",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "HARD",
                "text":
                "If the battery temperature increases, the system _____ reduce power.",
                "a": "will",
                "b": "would",
                "c": "has",
                "d": "was",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "MEDIUM",
                "text":
                "The aircraft components _____ inspected regularly.",
                "a": "are",
                "b": "is",
                "c": "was",
                "d": "has",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "MEDIUM",
                "text":
                "The pilot reported that the engine _____ unusual noise.",
                "a": "produced",
                "b": "produce",
                "c": "producing",
                "d": "has produce",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "HARD",
                "text":
                "The data collected during the experiment _____ analyzed.",
                "a": "were",
                "b": "was",
                "c": "is",
                "d": "has",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "HARD",
                "text":
                "The aircraft can operate safely if all systems _____ functional.",
                "a": "remain",
                "b": "remains",
                "c": "remained",
                "d": "remaining",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "MEDIUM",
                "text":
                "The purpose of this study is _____ the aerodynamic performance.",
                "a": "to investigate",
                "b": "investigated",
                "c": "investigating",
                "d": "investigation",
                "answer": "A",
            },

            {
                "domain": "Aerospace Grammar",
                "skill": "GRAMMAR",
                "level": "HARD",
                "text":
                "The new control algorithm _____ improved flight stability.",
                "a": "has",
                "b": "have",
                "c": "having",
                "d": "were",
                "answer": "A",
            },


            # ==========================
            # ICAO AVIATION ENGLISH
            # ==========================

            {
                "domain": "ICAO Aviation English",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The word 'departure' refers to:",
                "a": "leaving an airport",
                "b": "landing an aircraft",
                "c": "repairing an aircraft",
                "d": "parking a vehicle",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The word 'arrival' means:",
                "a": "reaching a destination",
                "b": "starting an engine",
                "c": "increasing speed",
                "d": "changing altitude",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The phrase 'maintain altitude' means:",
                "a": "keep the current altitude",
                "b": "increase altitude rapidly",
                "c": "reduce engine power",
                "d": "change direction",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A runway is used for:",
                "a": "takeoff and landing",
                "b": "fuel production",
                "c": "aircraft design",
                "d": "engine testing only",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The main purpose of standard aviation phraseology is:",
                "a": "clear and safe communication",
                "b": "faster aircraft design",
                "c": "reducing fuel consumption",
                "d": "changing regulations",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'cleared for takeoff' means:",
                "a": "permission to begin takeoff",
                "b": "aircraft inspection completed",
                "c": "engine stopped",
                "d": "flight cancelled",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'taxi' in aviation refers to:",
                "a": "moving an aircraft on the ground",
                "b": "flying at high altitude",
                "c": "landing without runway",
                "d": "repairing aircraft",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "ICAO English proficiency requirements focus mainly on:",
                "a": "effective aviation communication",
                "b": "aircraft manufacturing",
                "c": "engine maintenance",
                "d": "airport construction",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A 'holding pattern' is:",
                "a": "a flight path used while waiting",
                "b": "an engine failure",
                "c": "a maintenance procedure",
                "d": "a runway inspection",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'Mayday' indicates:",
                "a": "a serious emergency",
                "b": "normal operation",
                "c": "routine communication",
                "d": "weather information",
                "answer": "A",
            },

            {
                "domain": "ICAO Aviation English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Aviation communication requires accuracy because:",
                "a": "misunderstanding can create safety risks",
                "b": "pilots need longer conversations",
                "c": "aircraft have no systems",
                "d": "weather is always predictable",
                "answer": "A",
            },


            # ==========================
            # ADVANCED AEROSPACE VOCABULARY
            # ==========================

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'aerodynamic efficiency' refers to:",
                "a": "the ability to produce useful aerodynamic performance with minimum losses",
                "b": "the weight of an aircraft",
                "c": "the amount of fuel stored",
                "d": "the size of an airport",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'drag' in aerodynamics means:",
                "a": "a force opposing motion through the air",
                "b": "an engine component",
                "c": "a navigation system",
                "d": "a structural material",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Lift is a force that acts:",
                "a": "perpendicular to the airflow direction",
                "b": "opposite to gravity only",
                "c": "along the fuselage",
                "d": "inside the engine",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The fuselage of an aircraft is:",
                "a": "the main body structure",
                "b": "the engine turbine",
                "c": "the landing gear only",
                "d": "the navigation computer",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'boundary layer separation' describes:",
                "a": "loss of attached airflow from a surface",
                "b": "engine shutdown",
                "c": "fuel leakage",
                "d": "structural failure",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The word 'robust' in engineering usually means:",
                "a": "able to operate reliably under different conditions",
                "b": "very lightweight",
                "c": "very expensive",
                "d": "completely automatic",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'degradation' in battery systems refers to:",
                "a": "gradual reduction in performance",
                "b": "increase in capacity",
                "c": "complete redesign",
                "d": "software installation",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'mission profile' describes:",
                "a": "the planned sequence of an aircraft mission",
                "b": "the aircraft color",
                "c": "the pilot's biography",
                "d": "the airport layout",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'feasibility analysis' means:",
                "a": "evaluation of whether a project can be successfully performed",
                "b": "aircraft painting process",
                "c": "engine manufacturing",
                "d": "pilot training",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'payload' refers to:",
                "a": "the useful load carried by an aircraft or spacecraft",
                "b": "the aircraft engine",
                "c": "the landing system",
                "d": "the fuel tank only",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'trajectory' is related to:",
                "a": "the path followed by a moving object",
                "b": "aircraft manufacturing",
                "c": "engine temperature",
                "d": "material strength",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'uncertainty quantification' refers to:",
                "a": "analysis of uncertainties affecting predictions",
                "b": "removing all sensors",
                "c": "increasing aircraft weight",
                "d": "changing flight regulations",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'stall' in aerodynamics means:",
                "a": "loss of lift due to flow separation",
                "b": "engine acceleration",
                "c": "normal cruise condition",
                "d": "fuel improvement",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'optimization' means:",
                "a": "finding the best solution according to defined objectives",
                "b": "removing all constraints",
                "c": "reducing research quality",
                "d": "avoiding calculations",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'simulation' refers to:",
                "a": "a computer-based representation of a real system",
                "b": "a physical repair",
                "c": "a flight ticket",
                "d": "a maintenance schedule",
                "answer": "A",
            },


            # ==========================
            # RESEARCH PAPER ENGLISH
            # ==========================

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "In a scientific paper, the 'abstract' provides:",
                "a": "a brief summary of the research",
                "b": "all experimental data",
                "c": "only references",
                "d": "author information",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The 'introduction' section usually explains:",
                "a": "background and motivation of the research",
                "b": "only numerical results",
                "c": "software installation steps",
                "d": "aircraft maintenance procedures",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "The main purpose of the methodology section is:",
                "a": "to describe how the research was performed",
                "b": "to introduce the authors",
                "c": "to summarize references only",
                "d": "to advertise equipment",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The phrase 'the results demonstrate that' means:",
                "a": "the results show evidence of something",
                "b": "the experiment was cancelled",
                "c": "the data was removed",
                "d": "the method was unknown",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The word 'investigate' in research papers means:",
                "a": "to study systematically",
                "b": "to ignore",
                "c": "to replace",
                "d": "to simplify",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
The objective of this study is to analyze the aerodynamic performance
of a modified airfoil under different operating conditions.

Question:
What is the objective of the study?
                """,
                "a": "Analyzing aerodynamic performance",
                "b": "Manufacturing an aircraft",
                "c": "Training pilots",
                "d": "Designing airports",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'experimental setup' refers to:",
                "a": "the arrangement of equipment used in an experiment",
                "b": "the final conclusion",
                "c": "the paper title",
                "d": "the reference list",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The word 'validate' in engineering research means:",
                "a": "to confirm accuracy using evidence",
                "b": "to remove data",
                "c": "to increase errors",
                "d": "to change objectives",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "Figures and tables in research papers are mainly used to:",
                "a": "present data clearly",
                "b": "replace all explanations",
                "c": "increase paper length",
                "d": "avoid analysis",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The phrase 'compared with previous studies' indicates:",
                "a": "comparison with earlier research",
                "b": "removal of references",
                "c": "a new experiment",
                "d": "software development",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
The proposed method improves prediction accuracy while reducing computational
cost.

Question:
What two advantages are mentioned?
                """,
                "a": "Higher accuracy and lower computational cost",
                "b": "Higher weight and higher cost",
                "c": "Lower accuracy and longer time",
                "d": "No improvement",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'significantly' in scientific writing means:",
                "a": "to a meaningful or important degree",
                "b": "without measurement",
                "c": "randomly",
                "d": "incorrectly",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "A 'limitation' of a study refers to:",
                "a": "a restriction or weakness of the research",
                "b": "a final result",
                "c": "a reference paper",
                "d": "a new discovery",
                "answer": "A",
            },

            {
                "domain": "Research Paper English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why are references important in scientific papers?",
                "a": "They support statements and acknowledge previous work",
                "b": "They replace experiments",
                "c": "They remove conclusions",
                "d": "They increase file size",
                "answer": "A",
            },


            # ==========================
            # ENGINEERING REPORT WRITING
            # ==========================

            {
                "domain": "Engineering Report Writing",
                "skill": "WRITING",
                "level": "MEDIUM",
                "text":
                "The purpose of an engineering report is to:",
                "a": "present technical information in a structured way",
                "b": "describe personal experiences only",
                "c": "replace calculations",
                "d": "avoid technical details",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The phrase 'the results show that' is commonly used to:",
                "a": "introduce findings",
                "b": "describe equipment failure",
                "c": "write references",
                "d": "define terminology",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'increase' means:",
                "a": "become larger or higher",
                "b": "become smaller",
                "c": "remain unchanged",
                "d": "disappear",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'decrease' means:",
                "a": "become lower or smaller",
                "b": "increase rapidly",
                "c": "remain constant",
                "d": "change randomly",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "READING",
                "level": "MEDIUM",
                "text":
                """
The experimental results indicate that increasing the angle of attack
increases lift up to a certain point.

Question:
What happens when the angle of attack increases?
                """,
                "a": "Lift increases until a certain limit",
                "b": "Lift always decreases",
                "c": "The aircraft stops immediately",
                "d": "Drag becomes zero",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "WRITING",
                "level": "HARD",
                "text":
                "Which sentence is more suitable for a technical report?",
                "a": "The obtained results demonstrate improved performance.",
                "b": "The results were really good.",
                "c": "The system was amazing.",
                "d": "Everything worked perfectly.",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'trend' in data analysis refers to:",
                "a": "a general direction of change",
                "b": "a measurement error only",
                "c": "a component failure",
                "d": "a random value",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The phrase 'remained constant' means:",
                "a": "did not change significantly",
                "b": "increased rapidly",
                "c": "decreased suddenly",
                "d": "became unstable",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "WRITING",
                "level": "HARD",
                "text":
                "A comparison section in an engineering report is used to:",
                "a": "compare different methods or results",
                "b": "introduce unrelated information",
                "c": "remove data",
                "d": "avoid discussion",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The phrase 'within acceptable limits' means:",
                "a": "inside allowed safety or performance ranges",
                "b": "outside all requirements",
                "c": "without measurement",
                "d": "completely failed",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
The proposed design reduces weight while maintaining structural strength.

Question:
What is the main advantage of the proposed design?
                """,
                "a": "Lower weight without reducing strength",
                "b": "Higher weight and lower strength",
                "c": "Removing structural analysis",
                "d": "Increasing manufacturing errors",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'approximately' means:",
                "a": "nearly or close to a value",
                "b": "exactly",
                "c": "never",
                "d": "incorrectly",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The phrase 'a significant improvement' means:",
                "a": "a noticeable and meaningful improvement",
                "b": "a small error",
                "c": "no change",
                "d": "a failure",
                "answer": "A",
            },

            {
                "domain": "Engineering Report Writing",
                "skill": "WRITING",
                "level": "HARD",
                "text":
                "Which phrase is suitable for describing future work?",
                "a": "Future studies will investigate additional conditions.",
                "b": "The experiment was bad.",
                "c": "The system is useless.",
                "d": "Nothing can be improved.",
                "answer": "A",
            },


            # ==========================
            # eVTOL / ELECTRIC AIRCRAFT ENGLISH
            # ==========================

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'electric propulsion' refers to:",
                "a": "propulsion systems powered by electrical energy",
                "b": "traditional fuel engines only",
                "c": "aircraft structures",
                "d": "airport operations",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A battery's capacity describes:",
                "a": "the amount of energy it can store",
                "b": "its physical color",
                "c": "its manufacturing location",
                "d": "the aircraft speed",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'state of charge (SOC)' indicates:",
                "a": "the remaining battery charge level",
                "b": "the aircraft weight",
                "c": "the engine temperature",
                "d": "the altitude",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'state of health (SOH)' describes:",
                "a": "the current condition of a battery compared with its original condition",
                "b": "the aircraft location",
                "c": "the pilot experience",
                "d": "the flight route",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "One major challenge of electric aircraft is:",
                "a": "limited energy storage compared with fuel systems",
                "b": "lack of aerodynamic principles",
                "c": "absence of control systems",
                "d": "no need for batteries",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'range' in aircraft performance refers to:",
                "a": "the maximum distance an aircraft can travel",
                "b": "the aircraft color",
                "c": "the engine size",
                "d": "the runway width",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Energy management in electric aircraft focuses on:",
                "a": "efficient use and monitoring of available energy",
                "b": "changing aircraft shape",
                "c": "painting the aircraft",
                "d": "airport design",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'hybrid propulsion' means:",
                "a": "combination of different propulsion technologies",
                "b": "only electric motors",
                "c": "only hydraulic systems",
                "d": "no propulsion system",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Electric aircraft require advanced battery systems because batteries
must provide sufficient energy while maintaining acceptable weight.

Question:
Why are advanced batteries required?
                """,
                "a": "To provide enough energy with acceptable weight",
                "b": "To increase aircraft noise",
                "c": "To replace aerodynamic design",
                "d": "To remove safety systems",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'thermal management' refers to:",
                "a": "controlling and managing temperature",
                "b": "increasing aircraft weight",
                "c": "changing communication systems",
                "d": "improving passenger comfort only",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is battery monitoring important in electric aircraft?",
                "a": "It helps ensure safe and reliable operation",
                "b": "It eliminates the need for pilots",
                "c": "It increases aircraft noise",
                "d": "It changes aerodynamic forces",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'autonomous' means:",
                "a": "able to operate with reduced human control",
                "b": "unable to move",
                "c": "powered only by fuel",
                "d": "controlled manually only",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Safety analysis in aircraft design is performed to:",
                "a": "identify and reduce potential risks",
                "b": "increase failures",
                "c": "remove all requirements",
                "d": "avoid testing",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'redundancy' in aerospace systems means:",
                "a": "having backup components to improve reliability",
                "b": "removing all systems",
                "c": "reducing safety",
                "d": "decreasing performance",
                "answer": "A",
            },

            {
                "domain": "Electric Aircraft English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Urban air mobility vehicles require reliable propulsion,
efficient energy systems, and advanced control methods.

Question:
Which three areas are mentioned?
                """,
                "a": "Propulsion, energy systems, and control methods",
                "b": "Airport design, weather, and tourism",
                "c": "Manufacturing, painting, and marketing",
                "d": "Fuel production, roads, and traffic",
                "answer": "A",
            },


            # ==========================
            # FLIGHT TEST ENGLISH
            # ==========================

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The purpose of a flight test is to:",
                "a": "evaluate aircraft performance and behavior",
                "b": "design airports",
                "c": "produce fuel",
                "d": "train passengers",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'flight envelope' refers to:",
                "a": "the range of operating conditions where an aircraft can safely operate",
                "b": "the aircraft interior design",
                "c": "the pilot uniform",
                "d": "the airport area",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Telemetry is used to:",
                "a": "transmit measurement data from an aircraft to a ground station",
                "b": "increase aircraft weight",
                "c": "control airport traffic only",
                "d": "manufacture aircraft parts",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'performance' in aircraft testing refers to:",
                "a": "measurable characteristics such as speed, range, and efficiency",
                "b": "aircraft color",
                "c": "passenger service",
                "d": "airport location",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why are flight tests performed before aircraft certification?",
                "a": "To verify safety and performance requirements",
                "b": "To increase production cost",
                "c": "To remove regulations",
                "d": "To avoid analysis",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'test condition' means:",
                "a": "the specific situation under which a test is performed",
                "b": "the aircraft manufacturer",
                "c": "the pilot license",
                "d": "the aircraft price",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'validation' in flight testing means:",
                "a": "confirming that a model or system represents real behavior",
                "b": "changing aircraft design randomly",
                "c": "removing measurements",
                "d": "stopping experiments",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A sensor is used to:",
                "a": "measure physical parameters",
                "b": "produce fuel",
                "c": "replace the aircraft structure",
                "d": "control weather",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
During a flight test campaign, engineers collect data from sensors and compare
the measured results with simulation predictions.

Question:
Why do engineers compare measurements with simulations?
                """,
                "a": "To evaluate model accuracy",
                "b": "To increase aircraft weight",
                "c": "To remove sensors",
                "d": "To change the mission",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'stability' in flight dynamics describes:",
                "a": "the ability of an aircraft to maintain or recover its flight condition",
                "b": "the aircraft manufacturing cost",
                "c": "the fuel color",
                "d": "the airport capacity",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Flight test data analysis is important because:",
                "a": "it helps identify system behavior and possible issues",
                "b": "it eliminates engineering requirements",
                "c": "it replaces aircraft design",
                "d": "it avoids measurements",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'maneuver' refers to:",
                "a": "a controlled aircraft movement or operation",
                "b": "a maintenance document",
                "c": "a fuel component",
                "d": "a structural material",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'accuracy' refers to:",
                "a": "how close a measurement is to the true value",
                "b": "the aircraft speed",
                "c": "the engine size",
                "d": "the flight duration",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'repeatability' means:",
                "a": "obtaining similar results under the same conditions",
                "b": "changing test conditions every time",
                "c": "removing measurement systems",
                "d": "reducing aircraft safety",
                "answer": "A",
            },

            {
                "domain": "Flight Test English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Flight testing combines aircraft operation, instrumentation, data acquisition,
and engineering analysis to evaluate a new design.

Question:
Which activities are included in flight testing?
                """,
                "a": "Operation, measurement, data collection, and analysis",
                "b": "Only aircraft painting",
                "c": "Only airport management",
                "d": "Only passenger operations",
                "answer": "A",
            },


            # ==========================
            # UAV ENGLISH
            # ==========================

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The abbreviation UAV stands for:",
                "a": "Unmanned Aerial Vehicle",
                "b": "Universal Aircraft Velocity",
                "c": "Unified Aviation Value",
                "d": "Uncontrolled Air Vehicle",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A UAS consists of:",
                "a": "an unmanned aircraft and its supporting systems",
                "b": "only the aircraft structure",
                "c": "only the pilot station",
                "d": "only the communication system",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "An autopilot system is used to:",
                "a": "automatically control aircraft functions",
                "b": "increase aircraft weight",
                "c": "replace the structure",
                "d": "produce fuel",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'navigation' refers to:",
                "a": "determining position and route",
                "b": "changing aircraft color",
                "c": "repairing engines",
                "d": "manufacturing materials",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A GPS receiver provides information about:",
                "a": "position and location",
                "b": "engine temperature only",
                "c": "fuel production",
                "d": "structural strength",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The main purpose of mission planning is:",
                "a": "to define the tasks and flight objectives",
                "b": "to change aircraft materials",
                "c": "to remove sensors",
                "d": "to reduce communication",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A sensor in a UAV is used to:",
                "a": "collect information about the environment or aircraft state",
                "b": "increase aircraft size",
                "c": "replace batteries",
                "d": "control airports",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'autonomous flight' means:",
                "a": "flight operation with limited human intervention",
                "b": "flight without any control system",
                "c": "manual flight only",
                "d": "flight without navigation",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Modern UAVs use sensors, communication systems, and onboard computers
to perform different missions.

Question:
Which systems are mentioned in the text?
                """,
                "a": "Sensors, communication systems, and onboard computers",
                "b": "Only engines",
                "c": "Only landing gear",
                "d": "Only fuel systems",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'payload' in UAV applications refers to:",
                "a": "equipment carried to perform a mission",
                "b": "the aircraft paint",
                "c": "the pilot seat",
                "d": "the runway surface",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'communication link' refers to:",
                "a": "the connection between UAV and ground systems",
                "b": "the aircraft structure",
                "c": "the fuel system",
                "d": "the aerodynamic surface",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is reliable communication important for UAVs?",
                "a": "To maintain safe control and data exchange",
                "b": "To increase aircraft weight",
                "c": "To remove navigation systems",
                "d": "To reduce mission capability",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'altitude' means:",
                "a": "height above a reference level",
                "b": "aircraft speed",
                "c": "fuel quantity",
                "d": "wing length",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'obstacle avoidance' means:",
                "a": "detecting and avoiding objects during flight",
                "b": "increasing aircraft weight",
                "c": "removing sensors",
                "d": "stopping communication",
                "answer": "A",
            },

            {
                "domain": "UAV English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
A UAV navigation system combines GPS data, sensors, and control algorithms
to follow a planned trajectory.

Question:
What does the navigation system combine?
                """,
                "a": "GPS, sensors, and control algorithms",
                "b": "Fuel, engines, and passengers",
                "c": "Airports and roads",
                "d": "Materials and structures",
                "answer": "A",
            },


            # ==========================
            # SPACE MISSION ENGLISH
            # ==========================

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A satellite is:",
                "a": "an object placed in orbit around a celestial body",
                "b": "an aircraft engine",
                "c": "a ground vehicle",
                "d": "a runway system",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'orbit' refers to:",
                "a": "the path followed by an object around another object",
                "b": "the aircraft landing procedure",
                "c": "the engine operation",
                "d": "the manufacturing process",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A launch vehicle is used to:",
                "a": "carry spacecraft into space",
                "b": "repair satellites",
                "c": "control aircraft engines",
                "d": "design airports",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The payload of a spacecraft is:",
                "a": "the equipment or instruments carried for a mission",
                "b": "the fuel tank only",
                "c": "the launch pad",
                "d": "the communication tower",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The main purpose of a satellite mission is:",
                "a": "to perform specific tasks such as communication or observation",
                "b": "to increase aircraft speed",
                "c": "to replace airports",
                "d": "to manufacture engines",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A ground station is used to:",
                "a": "communicate with and control spacecraft",
                "b": "launch aircraft",
                "c": "produce fuel",
                "d": "repair runways",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'spacecraft' refers to:",
                "a": "a vehicle designed for space operation",
                "b": "a passenger aircraft",
                "c": "a military truck",
                "d": "a navigation map",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'telemetry' in space missions means:",
                "a": "transmission of spacecraft measurements to ground systems",
                "b": "changing satellite orbit manually",
                "c": "repairing spacecraft structures",
                "d": "designing launch vehicles",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
A satellite mission requires communication systems, power generation,
thermal control, and onboard computers.

Question:
Which systems are required for a satellite mission?
                """,
                "a": "Communication, power, thermal control, and computers",
                "b": "Only engines",
                "c": "Only landing gear",
                "d": "Only fuel systems",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'mission control' refers to:",
                "a": "the center responsible for monitoring and managing missions",
                "b": "the spacecraft engine",
                "c": "the satellite material",
                "d": "the launch vehicle fuel",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'attitude control' in spacecraft refers to:",
                "a": "controlling spacecraft orientation",
                "b": "controlling passenger movement",
                "c": "changing orbit size only",
                "d": "fuel production",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is thermal control important in spacecraft?",
                "a": "To maintain suitable temperatures for onboard systems",
                "b": "To increase spacecraft weight",
                "c": "To remove communication systems",
                "d": "To reduce mission duration",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'deployment' in space missions means:",
                "a": "placing a spacecraft or component into its operational position",
                "b": "destroying equipment",
                "c": "ending a mission",
                "d": "repairing aircraft",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'redundant system' means:",
                "a": "a backup system designed to improve reliability",
                "b": "an unnecessary mission",
                "c": "a failed component",
                "d": "a temporary signal",
                "answer": "A",
            },

            {
                "domain": "Space Mission English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Space missions require careful planning because spacecraft operate in harsh
environments and cannot easily be repaired after launch.

Question:
Why is careful planning important in space missions?
                """,
                "a": "Because spacecraft operate in difficult environments",
                "b": "Because spacecraft are always close to Earth",
                "c": "Because repairs are simple",
                "d": "Because communication is unnecessary",
                "answer": "A",
            },


            # ==========================
            # AERODYNAMICS TERMINOLOGY
            # ==========================

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Aerodynamics is the study of:",
                "a": "airflow and forces acting on moving bodies",
                "b": "fuel production",
                "c": "aircraft manufacturing only",
                "d": "airport management",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'airfoil' refers to:",
                "a": "a shape designed to generate aerodynamic forces",
                "b": "an aircraft engine",
                "c": "a communication system",
                "d": "a landing device",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The angle of attack is the angle between:",
                "a": "the airfoil reference line and incoming airflow",
                "b": "the aircraft and runway",
                "c": "the engine and fuel tank",
                "d": "the wing and fuselage",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The Reynolds number is related to:",
                "a": "flow characteristics and viscosity effects",
                "b": "aircraft price",
                "c": "fuel capacity only",
                "d": "pilot experience",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The main purpose of CFD simulations is to:",
                "a": "analyze fluid flow using computational methods",
                "b": "replace aircraft structures",
                "c": "control airport traffic",
                "d": "manufacture engines",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'viscosity' describes:",
                "a": "the resistance of a fluid to deformation",
                "b": "aircraft weight",
                "c": "engine power",
                "d": "flight altitude",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Flow separation occurs when:",
                "a": "airflow detaches from a surface",
                "b": "fuel stops flowing",
                "c": "the aircraft lands",
                "d": "the engine starts",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The drag coefficient represents:",
                "a": "a dimensionless measure of aerodynamic drag",
                "b": "engine temperature",
                "c": "fuel consumption only",
                "d": "structural strength",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Boundary layer analysis is important because it affects:",
                "a": "drag and flow separation behavior",
                "b": "fuel storage capacity",
                "c": "communication systems",
                "d": "passenger comfort only",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'compressibility effects' refers to:",
                "a": "changes in flow behavior due to density variations",
                "b": "aircraft painting",
                "c": "structural damage",
                "d": "fuel leakage",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Mach number is defined as:",
                "a": "the ratio of flow velocity to speed of sound",
                "b": "aircraft weight divided by fuel",
                "c": "wing length ratio",
                "d": "engine power ratio",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Increasing the angle of attack can increase lift. However, beyond a critical
value, flow separation occurs and lift decreases.

Question:
What happens beyond the critical angle of attack?
                """,
                "a": "Lift decreases due to flow separation",
                "b": "Lift increases indefinitely",
                "c": "Drag becomes zero",
                "d": "The aircraft stops experiencing airflow",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'optimization' in aerodynamic design means:",
                "a": "finding the best design according to objectives and constraints",
                "b": "removing all analysis",
                "c": "increasing errors",
                "d": "avoiding simulations",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'wake' behind an aircraft refers to:",
                "a": "the disturbed airflow region behind the aircraft",
                "b": "the aircraft cockpit",
                "c": "the fuel system",
                "d": "the navigation computer",
                "answer": "A",
            },

            {
                "domain": "Aerodynamics Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Wind tunnel testing is performed to:",
                "a": "study aerodynamic behavior under controlled conditions",
                "b": "produce aircraft fuel",
                "c": "replace all flight operations",
                "d": "train pilots",
                "answer": "A",
            },


            # ==========================
            # FLIGHT DYNAMICS & CONTROL TERMINOLOGY
            # ==========================

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Flight dynamics is the study of:",
                "a": "aircraft motion and response to forces and moments",
                "b": "fuel manufacturing",
                "c": "airport management",
                "d": "aircraft painting",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Aircraft stability refers to:",
                "a": "the ability to maintain or recover its flight condition",
                "b": "the aircraft production cost",
                "c": "the amount of fuel",
                "d": "the passenger capacity",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The elevator control surface mainly controls:",
                "a": "pitch motion",
                "b": "roll motion",
                "c": "yaw motion",
                "d": "engine speed",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The ailerons are used to control:",
                "a": "roll motion",
                "b": "fuel flow",
                "c": "engine temperature",
                "d": "altitude only",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The rudder controls aircraft:",
                "a": "yaw motion",
                "b": "pitch motion",
                "c": "engine thrust",
                "d": "fuel consumption",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A feedback control system uses:",
                "a": "measured output information to adjust system behavior",
                "b": "only fuel information",
                "c": "only structural data",
                "d": "no measurements",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "An actuator is a device that:",
                "a": "converts control commands into physical movement",
                "b": "stores fuel",
                "c": "measures temperature only",
                "d": "produces lift",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A sensor is used in control systems to:",
                "a": "measure system states or variables",
                "b": "generate thrust",
                "c": "increase aircraft weight",
                "d": "replace actuators",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'attitude' in aerospace refers to:",
                "a": "the orientation of an aircraft relative to a reference frame",
                "b": "aircraft weight",
                "c": "fuel quantity",
                "d": "engine size",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'state variable' refers to:",
                "a": "a variable describing the condition of a dynamic system",
                "b": "a manufacturing tool",
                "c": "an airport facility",
                "d": "a fuel component",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The purpose of an autopilot system is:",
                "a": "to automatically control aircraft functions",
                "b": "to increase aircraft weight",
                "c": "to replace propulsion systems",
                "d": "to remove sensors",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The word 'trim' in flight control means:",
                "a": "adjusting controls to maintain desired flight conditions",
                "b": "stopping the aircraft",
                "c": "reducing engine power completely",
                "d": "removing control surfaces",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
A flight control system receives information from sensors, processes the data,
and sends commands to actuators.

Question:
What are the main components mentioned?
                """,
                "a": "Sensors, processing system, and actuators",
                "b": "Fuel tanks and engines only",
                "c": "Wings and landing gear only",
                "d": "Passengers and cabin systems",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'dynamic response' describes:",
                "a": "how a system changes over time after an input",
                "b": "the aircraft color",
                "c": "the manufacturing cost",
                "d": "the fuel capacity",
                "answer": "A",
            },

            {
                "domain": "Flight Dynamics and Control Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is stability analysis important in aircraft design?",
                "a": "To ensure safe and predictable aircraft behavior",
                "b": "To increase manufacturing errors",
                "c": "To eliminate control systems",
                "d": "To reduce aerodynamic analysis",
                "answer": "A",
            },


            # ==========================
            # PROPULSION TERMINOLOGY
            # ==========================

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Aircraft propulsion is related to:",
                "a": "generating thrust to move an aircraft",
                "b": "designing airports",
                "c": "controlling passengers",
                "d": "manufacturing wings only",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Thrust is:",
                "a": "the force produced by a propulsion system",
                "b": "the aircraft weight",
                "c": "the wing area",
                "d": "the fuel temperature",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A jet engine produces thrust by:",
                "a": "accelerating a mass of air or exhaust gases",
                "b": "increasing aircraft weight",
                "c": "reducing airflow completely",
                "d": "stopping combustion",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The compressor in a gas turbine engine is used to:",
                "a": "increase the pressure of incoming air",
                "b": "cool the aircraft cabin",
                "c": "generate electricity only",
                "d": "control landing gear",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The turbine section of a jet engine:",
                "a": "extracts energy from hot gases",
                "b": "stores fuel",
                "c": "produces lift",
                "d": "controls navigation",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Combustion in an aircraft engine refers to:",
                "a": "the process of burning fuel to release energy",
                "b": "cooling the engine",
                "c": "reducing airflow",
                "d": "controlling flight attitude",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A propeller generates thrust by:",
                "a": "accelerating air using rotating blades",
                "b": "burning fuel directly",
                "c": "changing aircraft structure",
                "d": "controlling altitude",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Specific fuel consumption indicates:",
                "a": "fuel efficiency of a propulsion system",
                "b": "aircraft weight",
                "c": "engine color",
                "d": "wing dimensions",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'efficiency' describes:",
                "a": "how effectively energy is converted into useful output",
                "b": "the aircraft size",
                "c": "the runway length",
                "d": "the pilot experience",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is thermal management important in propulsion systems?",
                "a": "To maintain safe operating temperatures",
                "b": "To increase fuel consumption",
                "c": "To remove combustion",
                "d": "To reduce thrust",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'bypass ratio' is associated with:",
                "a": "turbofan engine performance",
                "b": "aircraft structure",
                "c": "flight control systems",
                "d": "navigation systems",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
A turbofan engine combines a core engine with a fan section.
The fan accelerates a large amount of air and improves efficiency.

Question:
What is one advantage of the fan section?
                """,
                "a": "Improving propulsion efficiency",
                "b": "Reducing aircraft control",
                "c": "Removing combustion",
                "d": "Replacing the wing",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Electric propulsion uses:",
                "a": "electric motors powered by electrical energy",
                "b": "only combustion chambers",
                "c": "hydraulic systems only",
                "d": "mechanical fuel pumps only",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "One challenge of electric propulsion is:",
                "a": "energy storage limitations",
                "b": "lack of aerodynamic forces",
                "c": "absence of control systems",
                "d": "no requirement for batteries",
                "answer": "A",
            },

            {
                "domain": "Propulsion Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'power-to-weight ratio' describes:",
                "a": "available power compared with system weight",
                "b": "fuel color",
                "c": "aircraft length",
                "d": "engine temperature",
                "answer": "A",
            },


            # ==========================
            # STRUCTURES & MATERIALS TERMINOLOGY
            # ==========================

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Aircraft structures are designed to:",
                "a": "support loads and maintain structural integrity",
                "b": "produce fuel",
                "c": "control weather",
                "d": "generate communication signals",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A load in structural engineering is:",
                "a": "a force or moment applied to a structure",
                "b": "the aircraft color",
                "c": "the fuel type",
                "d": "the flight route",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Stress is defined as:",
                "a": "force divided by the area over which it acts",
                "b": "total aircraft weight",
                "c": "engine power",
                "d": "flight altitude",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Strain represents:",
                "a": "the deformation of a material under load",
                "b": "the aircraft speed",
                "c": "the fuel consumption",
                "d": "the engine temperature",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Structural analysis is performed to:",
                "a": "evaluate how structures respond to applied loads",
                "b": "increase aircraft weight",
                "c": "remove safety requirements",
                "d": "design airport systems",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Composite materials are:",
                "a": "materials made by combining different materials",
                "b": "only metallic materials",
                "c": "liquid fuels",
                "d": "electronic components",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "One advantage of composite materials is:",
                "a": "high strength-to-weight ratio",
                "b": "high fuel consumption",
                "c": "low aerodynamic efficiency",
                "d": "poor durability",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Fatigue failure occurs due to:",
                "a": "repeated loading over time",
                "b": "single color change",
                "c": "fuel production",
                "d": "communication errors",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is fatigue analysis important in aircraft design?",
                "a": "Because aircraft structures experience repeated loads during operation",
                "b": "Because aircraft never experience loads",
                "c": "Because materials are unlimited",
                "d": "Because structures do not fail",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The Young's modulus describes:",
                "a": "the stiffness of a material",
                "b": "the fuel efficiency",
                "c": "the aircraft range",
                "d": "the engine thrust",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Finite Element Method (FEM) is used for:",
                "a": "numerical analysis of complex structures",
                "b": "controlling aircraft manually",
                "c": "producing fuel",
                "d": "measuring passenger comfort",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Aircraft designers use lightweight materials because reducing structural
weight can improve aircraft efficiency and performance.

Question:
Why are lightweight materials used?
                """,
                "a": "To improve efficiency and performance",
                "b": "To increase structural failures",
                "c": "To reduce safety",
                "d": "To increase fuel consumption",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'deformation' means:",
                "a": "change in shape caused by applied forces",
                "b": "aircraft navigation",
                "c": "engine operation",
                "d": "fuel storage",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'failure mode' refers to:",
                "a": "the way a component can fail",
                "b": "the aircraft mission",
                "c": "the flight route",
                "d": "the manufacturing location",
                "answer": "A",
            },

            {
                "domain": "Structures and Materials Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Structural testing is performed to:",
                "a": "verify that a design can withstand expected loads",
                "b": "increase material damage",
                "c": "remove analysis methods",
                "d": "avoid safety evaluation",
                "answer": "A",
            },


            # ==========================
            # CFD & NUMERICAL SIMULATION TERMINOLOGY
            # ==========================

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "CFD stands for:",
                "a": "Computational Fluid Dynamics",
                "b": "Computer Flight Design",
                "c": "Control Force Dynamics",
                "d": "Computational Fuel Development",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "CONCEPT",
                "level": "MEDIUM",
                "text":
                "CFD simulations are mainly used to:",
                "a": "analyze fluid flow behavior using numerical methods",
                "b": "manufacture aircraft components",
                "c": "control airport traffic",
                "d": "replace aircraft structures",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A computational mesh is:",
                "a": "a division of the flow domain into small elements",
                "b": "an aircraft communication system",
                "c": "a propulsion component",
                "d": "a flight control surface",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is mesh quality important in CFD?",
                "a": "Because it affects numerical accuracy and solution reliability",
                "b": "Because it changes aircraft color",
                "c": "Because it increases fuel capacity",
                "d": "Because it replaces experiments",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A solver in CFD is responsible for:",
                "a": "solving governing equations numerically",
                "b": "creating aircraft geometry only",
                "c": "controlling pilots",
                "d": "measuring fuel level",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Boundary conditions define:",
                "a": "the conditions applied at the boundaries of a computational domain",
                "b": "the aircraft manufacturing process",
                "c": "the pilot training program",
                "d": "the aircraft price",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "A turbulence model is used to:",
                "a": "represent the effects of turbulent flow",
                "b": "increase aircraft weight",
                "c": "remove airflow",
                "d": "design engines only",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The Navier-Stokes equations describe:",
                "a": "fluid motion and momentum conservation",
                "b": "aircraft manufacturing cost",
                "c": "pilot communication",
                "d": "satellite orbit",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A converged CFD solution means:",
                "a": "the numerical solution has reached a stable state",
                "b": "the mesh has disappeared",
                "c": "the equations are removed",
                "d": "the simulation has failed",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Validation of CFD results means:",
                "a": "comparing simulation results with experimental or reference data",
                "b": "changing the mesh randomly",
                "c": "removing equations",
                "d": "ignoring errors",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Numerical error refers to:",
                "a": "difference caused by approximation methods",
                "b": "aircraft weight",
                "c": "engine failure",
                "d": "fuel leakage",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
CFD analysis requires appropriate geometry, mesh generation,
boundary conditions, and numerical models to obtain reliable results.

Question:
Which factors are required for CFD analysis?
                """,
                "a": "Geometry, mesh, boundary conditions, and numerical models",
                "b": "Only aircraft color",
                "c": "Only engine fuel",
                "d": "Only flight altitude",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'steady-state simulation' means:",
                "a": "flow properties do not change with time",
                "b": "aircraft does not move",
                "c": "mesh is unnecessary",
                "d": "no equations are solved",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'transient simulation' refers to:",
                "a": "a simulation where flow changes with time",
                "b": "a simulation without equations",
                "c": "a simulation without boundary conditions",
                "d": "a simulation without results",
                "answer": "A",
            },

            {
                "domain": "CFD and Numerical Simulation Terminology",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why are experimental data important for CFD studies?",
                "a": "They help verify and improve confidence in numerical results",
                "b": "They replace all simulations",
                "c": "They remove physical laws",
                "d": "They eliminate mesh generation",
                "answer": "A",
            },


            # ==========================
            # AEROSPACE RESEARCH & SCIENTIFIC PAPER READING
            # ==========================

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "The abstract of a scientific paper provides:",
                "a": "a brief summary of the research",
                "b": "only experimental data",
                "c": "only references",
                "d": "the author's biography",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The introduction section usually explains:",
                "a": "research background and motivation",
                "b": "only final results",
                "c": "only equations",
                "d": "the publication cost",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The methodology section describes:",
                "a": "the methods and procedures used in the research",
                "b": "only the conclusion",
                "c": "the author's personal information",
                "d": "future publications only",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The results section presents:",
                "a": "research findings and obtained data",
                "b": "only background information",
                "c": "only references",
                "d": "research motivation",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The discussion section focuses on:",
                "a": "interpretation and analysis of results",
                "b": "only mathematical definitions",
                "c": "paper formatting",
                "d": "author information",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The conclusion section summarizes:",
                "a": "main findings and contributions of the research",
                "b": "only the introduction",
                "c": "only references",
                "d": "experimental equipment",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "A research gap refers to:",
                "a": "an unanswered problem or limitation in existing studies",
                "b": "a formatting error",
                "c": "a missing page number",
                "d": "a publication fee",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The purpose of a literature review is:",
                "a": "to analyze previous studies related to a research topic",
                "b": "to replace experiments",
                "c": "to remove references",
                "d": "to avoid scientific sources",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A citation in a scientific paper indicates:",
                "a": "reference to previous research",
                "b": "a measurement error",
                "c": "a simulation failure",
                "d": "a design change",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'peer review' means:",
                "a": "evaluation of research by experts in the field",
                "b": "translation of a paper",
                "c": "automatic publication",
                "d": "changing authors",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why are figures important in scientific papers?",
                "a": "They present complex information visually",
                "b": "They replace all explanations",
                "c": "They remove data analysis",
                "d": "They increase paper length only",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'validation' in a research paper means:",
                "a": "checking whether results agree with reliable references or experiments",
                "b": "removing all data",
                "c": "changing the research topic",
                "d": "ignoring errors",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
This study investigates the aerodynamic performance of an airfoil using
numerical simulations and experimental validation.

Question:
What are the main methods used in this study?
                """,
                "a": "Numerical simulation and experimental validation",
                "b": "Only manufacturing",
                "c": "Only flight training",
                "d": "Only theoretical discussion",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'parameter study' means:",
                "a": "investigating the effect of different variables on results",
                "b": "writing author information",
                "c": "removing equations",
                "d": "changing journal names",
                "answer": "A",
            },

            {
                "domain": "Scientific Paper Reading",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "A strong research contribution should:",
                "a": "provide new knowledge or improve existing methods",
                "b": "only repeat previous work",
                "c": "avoid analysis",
                "d": "ignore previous studies",
                "answer": "A",
            },


            # ==========================
            # ADVANCED AEROSPACE ACADEMIC VOCABULARY
            # ==========================

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Research methodology refers to:",
                "a": "the systematic approach used to conduct research",
                "b": "the aircraft manufacturing process",
                "c": "the flight control system",
                "d": "the airport operation",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "An experimental setup describes:",
                "a": "the equipment and procedure used in an experiment",
                "b": "the aircraft design only",
                "c": "the publication process",
                "d": "the flight schedule",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A simulation model is used to:",
                "a": "represent and analyze a real system using mathematical methods",
                "b": "replace all physical laws",
                "c": "remove experimental data",
                "d": "increase measurement errors",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The purpose of uncertainty analysis is:",
                "a": "to evaluate the effect of unknown factors on results",
                "b": "to remove all calculations",
                "c": "to increase errors",
                "d": "to avoid measurements",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Measurement accuracy describes:",
                "a": "how close a measured value is to the true value",
                "b": "the size of the equipment",
                "c": "the experiment duration",
                "d": "the number of researchers",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Precision refers to:",
                "a": "the consistency of repeated measurements",
                "b": "the aircraft speed",
                "c": "the engine power",
                "d": "the flight altitude",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Error analysis is performed to:",
                "a": "identify and quantify possible sources of error",
                "b": "remove all data",
                "c": "avoid validation",
                "d": "replace scientific methods",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The term 'optimization' means:",
                "a": "finding the best solution according to defined objectives",
                "b": "removing constraints",
                "c": "avoiding calculations",
                "d": "reducing accuracy",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "An optimization problem usually includes:",
                "a": "objective function, design variables, and constraints",
                "b": "only experimental images",
                "c": "only aircraft dimensions",
                "d": "only reference papers",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A design variable is:",
                "a": "a parameter that can be changed during optimization",
                "b": "a fixed physical law",
                "c": "a measurement error",
                "d": "a publication rule",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The objective function represents:",
                "a": "the quantity that should be minimized or maximized",
                "b": "the aircraft manufacturer",
                "c": "the experimental equipment",
                "d": "the research title",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
The researchers developed a numerical model and compared its predictions
with experimental measurements to evaluate model reliability.

Question:
Why were experimental measurements compared with numerical predictions?
                """,
                "a": "To evaluate the reliability of the numerical model",
                "b": "To increase measurement errors",
                "c": "To remove the model",
                "d": "To avoid analysis",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Machine learning in aerospace can be used for:",
                "a": "prediction, classification, and data analysis",
                "b": "replacing all engineering principles",
                "c": "removing sensors",
                "d": "eliminating physics",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Physics-informed machine learning combines:",
                "a": "data-driven methods with physical knowledge",
                "b": "only random data",
                "c": "only experimental errors",
                "d": "only aircraft geometry",
                "answer": "A",
            },

            {
                "domain": "Advanced Aerospace Academic Vocabulary",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'dataset' refers to:",
                "a": "a collection of data used for analysis or training",
                "b": "an aircraft component",
                "c": "a flight route",
                "d": "a material property",
                "answer": "A",
            },


            # ==========================
            # AEROSPACE SAFETY & CERTIFICATION ENGLISH
            # ==========================

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Aircraft certification is the process of:",
                "a": "confirming that an aircraft meets required safety standards",
                "b": "designing airport buildings",
                "c": "training passengers",
                "d": "increasing aircraft weight",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Airworthiness means:",
                "a": "an aircraft is safe and suitable for operation",
                "b": "an aircraft has maximum speed",
                "c": "an aircraft has a large cabin",
                "d": "an aircraft uses electric power",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Regulations in aviation are used to:",
                "a": "establish safety and operational requirements",
                "b": "increase aircraft noise",
                "c": "remove safety procedures",
                "d": "replace engineering analysis",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Safety assessment is performed to:",
                "a": "identify and evaluate potential risks",
                "b": "increase system failures",
                "c": "remove maintenance procedures",
                "d": "avoid testing",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Risk analysis focuses on:",
                "a": "identifying hazards and evaluating their consequences",
                "b": "changing aircraft color",
                "c": "increasing fuel consumption",
                "d": "designing airports",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A hazard is:",
                "a": "a condition that can cause harm or failure",
                "b": "a successful operation",
                "c": "a flight schedule",
                "d": "a design improvement",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Reliability refers to:",
                "a": "the probability that a system performs correctly over time",
                "b": "the aircraft appearance",
                "c": "the fuel quantity",
                "d": "the pilot experience",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is reliability important in aerospace systems?",
                "a": "Because failures can have serious consequences",
                "b": "Because aircraft do not need safety",
                "c": "Because systems are always simple",
                "d": "Because maintenance is unnecessary",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Maintenance is performed to:",
                "a": "keep aircraft systems safe and operational",
                "b": "increase failures",
                "c": "remove inspections",
                "d": "reduce safety",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Failure analysis is used to:",
                "a": "determine causes of system failures",
                "b": "increase operational risks",
                "c": "remove engineering data",
                "d": "avoid investigation",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Aerospace engineers perform risk assessments during the design process
to identify possible failures and improve system safety.

Question:
Why are risk assessments performed?
                """,
                "a": "To identify failures and improve safety",
                "b": "To increase system complexity",
                "c": "To remove regulations",
                "d": "To avoid testing",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'redundancy' in safety engineering means:",
                "a": "using backup components to improve reliability",
                "b": "removing important systems",
                "c": "reducing safety margins",
                "d": "eliminating testing",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Safety-critical systems require:",
                "a": "high reliability and strict verification",
                "b": "less testing",
                "c": "fewer requirements",
                "d": "no monitoring",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Verification means:",
                "a": "checking whether a system meets specified requirements",
                "b": "changing the design randomly",
                "c": "removing standards",
                "d": "ignoring results",
                "answer": "A",
            },

            {
                "domain": "Aerospace Safety and Certification English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Validation means:",
                "a": "confirming that a system satisfies its intended purpose",
                "b": "removing all requirements",
                "c": "stopping analysis",
                "d": "avoiding experiments",
                "answer": "A",
            },


            # ==========================
            # AEROSPACE MANUFACTURING & INDUSTRY ENGLISH
            # ==========================

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Aircraft manufacturing refers to:",
                "a": "the process of producing aircraft components and systems",
                "b": "the process of flying passengers",
                "c": "airport management",
                "d": "weather prediction",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "The assembly process involves:",
                "a": "putting different components together to create a final product",
                "b": "removing all components",
                "c": "testing only pilots",
                "d": "designing airports",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Quality control is performed to:",
                "a": "ensure products meet required standards",
                "b": "increase manufacturing errors",
                "c": "reduce safety",
                "d": "avoid inspection",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Inspection means:",
                "a": "examining a component to verify its condition",
                "b": "manufacturing fuel",
                "c": "controlling weather",
                "d": "designing flight routes",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is quality assurance important in aerospace manufacturing?",
                "a": "Because aircraft components must meet strict safety requirements",
                "b": "Because aircraft do not require testing",
                "c": "Because errors improve reliability",
                "d": "Because standards are unnecessary",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Additive manufacturing is also known as:",
                "a": "3D printing",
                "b": "fuel injection",
                "c": "flight testing",
                "d": "aircraft maintenance",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "One advantage of additive manufacturing is:",
                "a": "the ability to create complex lightweight structures",
                "b": "increasing material waste",
                "c": "reducing design flexibility",
                "d": "eliminating quality checks",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A production line is:",
                "a": "a sequence of manufacturing operations",
                "b": "a flight route",
                "c": "a navigation system",
                "d": "a communication satellite",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "A prototype is:",
                "a": "an initial model used for testing and evaluation",
                "b": "a final certified aircraft",
                "c": "a maintenance document",
                "d": "a flight regulation",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A component is:",
                "a": "a part of a larger system",
                "b": "a complete airport",
                "c": "a flight mission",
                "d": "a weather condition",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Aircraft manufacturers use advanced materials and manufacturing methods
to reduce weight and improve performance.

Question:
Why are advanced manufacturing methods used?
                """,
                "a": "To reduce weight and improve performance",
                "b": "To increase errors",
                "c": "To reduce safety",
                "d": "To eliminate testing",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Supply chain refers to:",
                "a": "the network involved in producing and delivering products",
                "b": "the aircraft control system",
                "c": "the flight path",
                "d": "the engine operation",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Computer-Aided Design (CAD) is used for:",
                "a": "creating and modifying engineering designs",
                "b": "controlling aircraft manually",
                "c": "measuring passenger comfort",
                "d": "predicting weather",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "Computer-Aided Manufacturing (CAM) is related to:",
                "a": "computer-assisted production processes",
                "b": "aircraft navigation",
                "c": "satellite communication",
                "d": "pilot training",
                "answer": "A",
            },

            {
                "domain": "Aerospace Manufacturing English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why is traceability important in aerospace manufacturing?",
                "a": "To track materials and production history",
                "b": "To increase manufacturing errors",
                "c": "To remove quality records",
                "d": "To avoid inspections",
                "answer": "A",
            },


            # ==========================
            # AEROSPACE MAINTENANCE & OPERATIONS ENGLISH
            # ==========================

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "EASY",
                "text":
                "Aircraft maintenance is performed to:",
                "a": "keep aircraft safe and operational",
                "b": "increase system failures",
                "c": "remove inspections",
                "d": "reduce reliability",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Inspection means:",
                "a": "checking aircraft components for condition and safety",
                "b": "changing flight routes",
                "c": "designing new airports",
                "d": "producing fuel",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "Troubleshooting is the process of:",
                "a": "finding and solving system problems",
                "b": "increasing failures",
                "c": "removing aircraft systems",
                "d": "changing aircraft appearance",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A maintenance manual provides:",
                "a": "instructions for inspection, repair, and operation",
                "b": "weather information",
                "c": "passenger information",
                "d": "airport design rules",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Why are maintenance procedures important?",
                "a": "They ensure safe and standardized aircraft operation",
                "b": "They increase operational risks",
                "c": "They remove safety requirements",
                "d": "They eliminate inspections",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A repair means:",
                "a": "restoring a damaged component to an acceptable condition",
                "b": "removing all systems",
                "c": "changing aircraft missions",
                "d": "reducing reliability",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'fault' refers to:",
                "a": "a malfunction or abnormal condition in a system",
                "b": "a successful operation",
                "c": "a flight route",
                "d": "a design improvement",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'preventive maintenance' means:",
                "a": "maintenance performed before failures occur",
                "b": "repair after complete failure only",
                "c": "removing inspections",
                "d": "ignoring system condition",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'corrective maintenance' refers to:",
                "a": "actions taken to fix detected problems",
                "b": "flight planning",
                "c": "aircraft design",
                "d": "pilot training",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "MEL stands for:",
                "a": "Minimum Equipment List",
                "b": "Maximum Engine Load",
                "c": "Maintenance Energy Level",
                "d": "Manual Equipment Location",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "The purpose of an MEL is:",
                "a": "to define which inoperative items may allow aircraft dispatch",
                "b": "to increase aircraft failures",
                "c": "to replace all maintenance manuals",
                "d": "to remove safety procedures",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "MEDIUM",
                "text":
                "A component replacement means:",
                "a": "removing a faulty part and installing another one",
                "b": "changing aircraft registration",
                "c": "modifying weather conditions",
                "d": "changing passenger seats only",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "READING",
                "level": "HARD",
                "text":
                """
Maintenance engineers use aircraft manuals and inspection procedures
to identify problems and perform corrective actions.

Question:
What do maintenance engineers use?
                """,
                "a": "Manuals and inspection procedures",
                "b": "Only flight schedules",
                "c": "Only weather reports",
                "d": "Only passenger information",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "VOCAB",
                "level": "HARD",
                "text":
                "The term 'serviceable' means:",
                "a": "a component is acceptable for operation",
                "b": "a component is damaged",
                "c": "a system is removed",
                "d": "a flight is cancelled",
                "answer": "A",
            },

            {
                "domain": "Aerospace Maintenance English",
                "skill": "CONCEPT",
                "level": "HARD",
                "text":
                "Documentation is important in aircraft maintenance because:",
                "a": "it provides traceability of maintenance actions",
                "b": "it increases failures",
                "c": "it removes responsibility",
                "d": "it replaces inspections",
                "answer": "A",
            },

        ]


        created = 0

        for item in questions:

            Question.objects.get_or_create(
                question_text=item["text"],
                defaults={
                    "owner": None,

                    "question_type": "MCQ",

                    "option_a": item["a"],
                    "option_b": item["b"],
                    "option_c": item["c"],
                    "option_d": item["d"],

                    "correct_answer": item["answer"],

                    "explanation": (
                        "Imported from aerospace ESP question bank."
                    ),

                    "question_language": "EN",
                    "options_language": "EN",

                    "skill": (
                        item.get("skill", "VOCAB")
                        if item.get("skill") in [
                            "VOCAB",
                            "GRAMMAR",
                            "READING",
                            "LISTENING",
                            "WRITING",
                            "SPEAKING",
                        ]
                        else "VOCAB"
                    ),

                    "aerospace_domain": (
                        item.get("domain", "General")
                        .replace(
                            "Aerospace ",
                            ""
                        )[:20]
                    ),

                    "difficulty": {
                        "EASY": "BASIC",
                        "MEDIUM": "INTERMEDIATE",
                        "HARD": "ADVANCED",
                    }.get(
                        item.get("level"),
                        "INTERMEDIATE"
                    ),

                    "source_type": "BOOTSTRAP",
                    "status": "APPROVED",
                    "visibility": "PUBLIC",
                }
            )

            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"All aerospace questions ready. Created: {created}"
            )
        )