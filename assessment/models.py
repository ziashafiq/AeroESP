from django.db import models


class Question(models.Model):

    class Skill(models.TextChoices):
        VOCABULARY = "VOCAB", "Technical Vocabulary"
        GRAMMAR = "GRAMMAR", "Grammar in Engineering Context"
        READING = "READING", "Technical Reading"

    class Domain(models.TextChoices):
        AERODYNAMICS = "AERO", "Aerodynamics"
        FLIGHT_DYNAMICS = "FLIGHT", "Flight Dynamics & Control"
        PROPULSION = "PROP", "Propulsion"

    class Difficulty(models.TextChoices):
        BASIC = "BASIC", "Basic"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    question_text = models.TextField()

    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)

    correct_answer = models.CharField(
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
    )

    skill = models.CharField(
        max_length=20,
        choices=Skill.choices,
    )

    aerospace_domain = models.CharField(
        max_length=20,
        choices=Domain.choices,
    )

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BASIC,
    )

    explanation = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.question_text[:80]