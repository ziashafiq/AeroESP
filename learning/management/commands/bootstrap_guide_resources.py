from django.core.management.base import BaseCommand

from learning.models import GuideResource


class Command(BaseCommand):

    help = "Create initial AeroESP guide resources"


    def handle(self, *args, **kwargs):

        guides = [

            {
                "title": "Cambridge Dictionary",
                "category": "ENGLISH",
                "description": "A reliable dictionary for English definitions, pronunciation and examples.",
                "website_url": "https://dictionary.cambridge.org/",
                "usage_instruction": "Use it for vocabulary meaning, pronunciation and example sentences.",
                "recommended_level": "A2-C1",
            },

            {
                "title": "Anki Vocabulary Learning",
                "category": "ENGLISH",
                "description": "A spaced repetition tool for vocabulary improvement.",
                "website_url": "https://apps.ankiweb.net/",
                "usage_instruction": "Create flashcards and review vocabulary regularly.",
                "recommended_level": "A2-C1",
            },

            {
                "title": "IELTS Official Resources",
                "category": "IELTS",
                "description": "Official IELTS preparation resources.",
                "website_url": "https://www.ielts.org/",
                "usage_instruction": "Use for understanding IELTS test structure and preparation.",
                "recommended_level": "B1-C1",
            },

            {
                "title": "ICAO Aviation English",
                "category": "AEROSPACE",
                "description": "Resources related to aviation English communication.",
                "website_url": "https://www.icao.int/",
                "usage_instruction": "Useful for aviation terminology and professional communication.",
                "recommended_level": "B1-C1",
            },

            {
                "title": "NASA Technical Reports",
                "category": "AEROSPACE",
                "description": "Technical aerospace reports and publications.",
                "website_url": "https://ntrs.nasa.gov/",
                "usage_instruction": "Practice technical reading using aerospace documents.",
                "recommended_level": "B2-C1",
            },

            {
                "title": "ChatGPT for Language Learning",
                "category": "AI",
                "description": "Using AI assistants for explanation, correction and language practice.",
                "website_url": "https://chat.openai.com/",
                "usage_instruction": "Use AI for grammar correction, vocabulary explanation and conversation practice.",
                "recommended_level": "A2-C1",
            },

        ]


        created = 0


        for item in guides:

            obj, is_created = GuideResource.objects.get_or_create(
                title=item["title"],
                defaults=item,
            )

            if is_created:
                created += 1
                self.stdout.write(
                    f"[CREATE] {obj.title}"
                )
            else:
                self.stdout.write(
                    f"[SKIP] {obj.title}"
                )


        self.stdout.write(
            self.style.SUCCESS(
                f"Guide resources ready. Created: {created}"
            )
        )