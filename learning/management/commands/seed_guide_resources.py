from django.core.management.base import BaseCommand
from django.db import transaction

from learning.models import GuideResource


# Every URL here was checked live before being added. They are all
# root or near-root pages of long-lived institutions rather than deep
# links into a section that gets reorganised, which is what keeps this
# list from rotting. Nothing invented: if a candidate could not be
# confirmed reachable, it was left out.
RESOURCES = [
    {
        "title": "Cambridge Dictionary",
        "category": "ENGLISH",
        "website_url": "https://dictionary.cambridge.org/",
        "description": (
            "Learner-focused dictionary giving pronunciation, CEFR "
            "level, grammar patterns and example sentences for each "
            "sense of a word, rather than a single translation."
        ),
        "usage_instruction": (
            "Look a new word up here before adding it to your own "
            "vocabulary list. Note the CEFR label - it tells you "
            "whether the word is worth learning at your current level."
        ),
        "recommended_level": "A2-C1",
    },
    {
        "title": "BBC Learning English",
        "category": "ENGLISH",
        "website_url": "https://www.bbc.co.uk/learningenglish",
        "description": (
            "Free graded lessons, audio and video from the BBC, "
            "organised by level and by language point, with "
            "transcripts for every recording."
        ),
        "usage_instruction": (
            "Use the transcripts actively: listen once without "
            "reading, once while reading, then once more without. It "
            "trains listening far harder than passive watching does."
        ),
        "recommended_level": "A2-C1",
    },
    {
        "title": "Purdue OWL - Online Writing Lab",
        "category": "ENGLISH",
        "website_url": "https://owl.purdue.edu/",
        "description": (
            "Purdue University's academic writing reference, covering "
            "sentence structure, paragraphing, citation styles and the "
            "conventions of technical and scientific writing."
        ),
        "usage_instruction": (
            "The section on academic writing style is the most "
            "relevant here - it explains the register expected in "
            "engineering reports and papers."
        ),
        "recommended_level": "B1-C1",
    },
    {
        "title": "IELTS Official Website",
        "category": "IELTS",
        "website_url": "https://ielts.org/",
        "description": (
            "The official IELTS site from the test's own partners, "
            "with the current test format, free practice material and "
            "the band descriptors examiners actually mark against."
        ),
        "usage_instruction": (
            "Read the band descriptors before practising. Knowing what "
            "separates band 6 from band 7 changes what you work on far "
            "more than another practice test does."
        ),
        "recommended_level": "B1-C1",
    },
    {
        "title": "NASA Technical Reports Server (NTRS)",
        "category": "AEROSPACE",
        "website_url": "https://ntrs.nasa.gov/",
        "description": (
            "Open archive of NASA's technical reports and conference "
            "papers - authentic aerospace engineering English as it is "
            "actually written by practising engineers."
        ),
        "usage_instruction": (
            "Search a topic you already understand technically. "
            "Meeting familiar content in unfamiliar English is how "
            "technical reading speed is built."
        ),
        "recommended_level": "B2-C2",
    },
    {
        "title": "SKYbrary Aviation Safety",
        "category": "AEROSPACE",
        "website_url": "https://skybrary.aero/",
        "description": (
            "Reference library of aviation safety knowledge, "
            "maintained with EUROCONTROL, ICAO and the Flight Safety "
            "Foundation. Articles define operational terminology in "
            "context."
        ),
        "usage_instruction": (
            "Useful as a technical glossary: most articles open by "
            "defining their term precisely, which is exactly the "
            "phrasing to learn."
        ),
        "recommended_level": "B2-C1",
    },
    {
        "title": "ICAO - International Civil Aviation Organization",
        "category": "AEROSPACE",
        "website_url": "https://www.icao.int/",
        "description": (
            "The UN agency that sets international aviation standards, "
            "including the Language Proficiency Requirements that "
            "define the English level required of flight crew and "
            "controllers."
        ),
        "usage_instruction": (
            "Look up the Language Proficiency Rating Scale to see how "
            "aviation English is assessed against six levels - a "
            "useful contrast with CEFR."
        ),
        "recommended_level": "B2-C1",
    },
    {
        "title": "Anki - Spaced Repetition Flashcards",
        "category": "ENGLISH",
        "website_url": "https://apps.ankiweb.net/",
        "description": (
            "Free, open-source flashcard software that schedules "
            "reviews by spaced repetition, showing each card just "
            "before you would forget it."
        ),
        "usage_instruction": (
            "Write cards from sentences you met in real reading, not "
            "from word lists. A term learned in the context of a "
            "technical paper is one you can actually use."
        ),
        "recommended_level": "All levels",
    },
    {
        "title": "Zotero - Reference Manager",
        "category": "RESEARCH",
        "website_url": "https://www.zotero.org/",
        "description": (
            "Free reference manager that collects sources from the "
            "browser and generates citations and bibliographies in any "
            "major style."
        ),
        "usage_instruction": (
            "Start using it from your first literature search rather "
            "than at writing-up time - retrofitting references to a "
            "finished draft is the slowest way to do it."
        ),
        "recommended_level": "B2-C2",
    },
]


class Command(BaseCommand):
    help = (
        "Populate the Guide Hub with vetted external learning "
        "resources. Idempotent: matches on title, so re-running "
        "refreshes the entries instead of duplicating them."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be written without touching the DB.",
        )

    def handle(self, *args, **options):

        if options["dry_run"]:

            self.stdout.write(
                "--- DRY RUN: nothing will be written ---\n"
            )

            for entry in RESOURCES:
                self.stdout.write(
                    f"  [{entry['category']:9s}] {entry['title']}"
                )
                self.stdout.write(
                    f"              {entry['website_url']}"
                )

            self.stdout.write(
                f"\n{len(RESOURCES)} resource(s) would be written."
            )
            return

        created = 0
        updated = 0

        with transaction.atomic():

            for entry in RESOURCES:

                fields = dict(entry)
                title = fields.pop("title")

                _, was_created = (
                    GuideResource.objects.update_or_create(
                        title=title,
                        defaults={
                            **fields,
                            "is_public": True,
                        },
                    )
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Guide resources: {created} created, "
                f"{updated} updated."
            )
        )

        self.stdout.write(
            f"Total public resources now: "
            f"{GuideResource.objects.filter(is_public=True).count()}"
        )
