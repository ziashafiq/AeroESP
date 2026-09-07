import csv

from django.core.management.base import BaseCommand

from research_review.models import ExpertReview


COLUMNS = [
    "blind_id",
    "reviewer_code",
    "construct_relevance",
    "technical_correctness",
    "linguistic_accuracy",
    "clarity_answerability",
    "source_fidelity",
    "distractor_quality",
    "cefr_alignment",
    "difficulty_alignment",
    "pedagogical_value",
    "overall_decision",
    "error_codes",
    "reviewer_confidence",
    "time_spent_seconds",
    "question_provenance",
    "display_order",
]


class Command(BaseCommand):
    help = (
        "Export the reviewer x question matrix as CSV - one row per "
        "review, identified by an anonymized reviewer_code rather "
        "than a username. Suitable as-is for I-CVI / S-CVI "
        "(Polit & Beck, 2006) computation."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--output",
            dest="output_path",
            help=(
                "File to write the CSV to. Omit to write to stdout "
                "(so 'manage.py export_review_matrix > file.csv' "
                "also works)."
            ),
        )

        parser.add_argument(
            "--include-drafts",
            action="store_true",
            help=(
                "Include reviews that have not been finalized. "
                "Default: finalized reviews only, since a draft's "
                "EVAL_V1 scores may be incomplete or null and would "
                "otherwise silently pollute a CVI matrix."
            ),
        )

    def handle(self, *args, **options):

        reviews = (
            ExpertReview.objects
            .select_related(
                "assignment",
                "assignment__reviewer",
                "assignment__question",
            )
            .order_by(
                "assignment__question__blind_id",
                "assignment__reviewer__reviewer_code",
            )
        )

        if not options["include_drafts"]:
            reviews = reviews.filter(is_finalized=True)

        output_path = options["output_path"]

        if output_path:

            handle = open(
                output_path,
                "w",
                newline="",
                encoding="utf-8",
            )

        else:

            # The stream self.stdout wraps, not self.stdout itself:
            # OutputWrapper.write() appends its own newline on every
            # call, which would double up with the one csv.writer
            # already adds per row. Going one level down also means
            # `call_command(..., stdout=buffer)` in tests is honoured
            # (self.stdout._out is buffer there), unlike writing to
            # sys.stdout directly.
            handle = self.stdout._out

        try:

            writer = csv.writer(handle)

            writer.writerow(COLUMNS)

            row_count = 0

            for review in reviews.iterator():

                writer.writerow(
                    self._row(review)
                )

                row_count += 1

        finally:

            if output_path:
                handle.close()

        if output_path:

            self.stderr.write(
                self.style.SUCCESS(
                    f"Wrote {row_count} row(s) to {output_path}"
                )
            )

    def _row(self, review):

        assignment = review.assignment
        question = assignment.question
        reviewer = assignment.reviewer

        return [
            question.blind_id,
            reviewer.reviewer_code,
            review.construct_relevance,
            review.technical_correctness,
            review.linguistic_accuracy,
            review.clarity_answerability,
            review.source_fidelity,
            review.distractor_quality,
            review.cefr_alignment,
            review.difficulty_alignment,
            review.pedagogical_value,
            review.overall_decision,
            # A pipe-joined string, not the raw list - a bare Python
            # list ("['T1', 'D2']") is awkward to read in a CSV cell
            # and awkward for a stats package to split back apart.
            "|".join(review.error_codes),
            review.reviewer_confidence,
            review.time_spent_seconds,
            question.question_provenance,
            assignment.display_order,
        ]
