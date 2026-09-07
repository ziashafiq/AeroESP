import csv
import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from research_review.models import (
    ExpertReviewerProfile,
    ReviewAssignment,
    ResearchQuestion,
)


class Command(BaseCommand):
    help = (
        "Randomly assign K reviewers to each research question, "
        "balanced across active reviewers, with a reproducible seed."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--csv",
            dest="csv_path",
            help=(
                "Path to a CSV of questions to assign. A 'blind_id' "
                "column is used if present; otherwise the first "
                "column on each row is read."
            ),
        )

        parser.add_argument(
            "--blind-ids",
            dest="blind_ids",
            help=(
                "Comma-separated blind_id list, as an alternative to "
                "--csv (e.g. for a quick manual batch)."
            ),
        )

        parser.add_argument(
            "--k",
            type=int,
            default=3,
            help=(
                "How many reviewers to assign per question "
                "(default: 3, for redundancy)."
            ),
        )

        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help=(
                "Random seed. Omit to get a fresh one each run - it "
                "is still printed, so any run's exact assignment can "
                "be reproduced afterward by passing it back in "
                "(--seed=<the printed value>)."
            ),
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Print the assignment table and balance summary "
                "without writing anything to the database."
            ),
        )

    # -----------------------------------------------------
    # Input resolution
    # -----------------------------------------------------

    def _load_blind_ids(self, options):

        csv_path = options["csv_path"]
        inline = options["blind_ids"]

        if csv_path and inline:
            raise CommandError(
                "Pass either --csv or --blind-ids, not both."
            )

        if not csv_path and not inline:
            raise CommandError(
                "One of --csv or --blind-ids is required."
            )

        if inline:

            blind_ids = [
                value.strip()
                for value in inline.split(",")
                if value.strip()
            ]

        else:

            try:
                with open(
                    csv_path,
                    newline="",
                    encoding="utf-8-sig",
                ) as handle:

                    reader = csv.DictReader(handle)

                    if reader.fieldnames and (
                        "blind_id" in reader.fieldnames
                    ):

                        blind_ids = [
                            row["blind_id"].strip()
                            for row in reader
                            if row.get("blind_id", "").strip()
                        ]

                    else:
                        # No header, or no blind_id column: fall back
                        # to one blind_id per line, first column only.
                        handle.seek(0)

                        blind_ids = [
                            line.split(",")[0].strip()
                            for line in handle
                            if line.strip()
                        ]

            except OSError as error:
                raise CommandError(
                    f"Could not read {csv_path}: {error}"
                )

        if not blind_ids:
            raise CommandError(
                "No blind_id values were found in the input."
            )

        # De-duplicated, order preserved - a question named twice in
        # the input must not be assigned twice as hard as one named
        # once.
        seen = set()
        deduplicated = []

        for blind_id in blind_ids:

            if blind_id not in seen:
                seen.add(blind_id)
                deduplicated.append(blind_id)

        return deduplicated

    # -----------------------------------------------------
    # Assignment plan
    # -----------------------------------------------------

    def _build_plan(self, questions, reviewers, k, seed):
        """
        A sliding window over a once-shuffled reviewer list: reviewer
        i is included in question j's set whenever
        (j - i) mod N < K. Every reviewer therefore appears in exactly
        K of every N consecutive questions, which bounds the largest
        and smallest per-reviewer load to differ by at most 1
        regardless of how many questions there are.

        Returns {reviewer: [(question, display_order), ...]}.
        """

        rng = random.Random(seed)

        shuffled_reviewers = list(reviewers)
        rng.shuffle(shuffled_reviewers)

        n = len(shuffled_reviewers)

        assignments_by_reviewer = {
            reviewer: []
            for reviewer in shuffled_reviewers
        }

        for index, question in enumerate(questions):

            for offset in range(k):

                reviewer = shuffled_reviewers[
                    (index + offset) % n
                ]

                assignments_by_reviewer[reviewer].append(
                    question
                )

        # Each reviewer sees their own questions in an independently
        # randomised order, derived from the same seed so the whole
        # plan stays reproducible from one number.
        plan = {}

        for reviewer, assigned_questions in (
            assignments_by_reviewer.items()
        ):

            # random.Random() only accepts None/int/float/str/bytes -
            # a string combining both values is the simplest way to
            # get a distinct, still fully seed-derived RNG per
            # reviewer.
            reviewer_rng = random.Random(
                f"{seed}:{reviewer.pk}"
            )

            order = list(assigned_questions)
            reviewer_rng.shuffle(order)

            plan[reviewer] = [
                (question, position)
                for position, question in enumerate(
                    order,
                    start=1,
                )
            ]

        return plan

    # -----------------------------------------------------
    # Entry point
    # -----------------------------------------------------

    def handle(self, *args, **options):

        blind_ids = self._load_blind_ids(options)

        k = options["k"]

        if k < 1:
            raise CommandError("--k must be at least 1.")

        questions = list(
            ResearchQuestion.objects.filter(
                blind_id__in=blind_ids
            )
        )

        found_ids = {q.blind_id for q in questions}
        missing_ids = [
            blind_id
            for blind_id in blind_ids
            if blind_id not in found_ids
        ]

        if missing_ids:
            raise CommandError(
                "Unknown blind_id value(s): "
                + ", ".join(missing_ids)
            )

        # Preserve input order, not queryset order.
        questions_by_id = {q.blind_id: q for q in questions}
        questions = [
            questions_by_id[blind_id]
            for blind_id in blind_ids
        ]

        reviewers = list(
            ExpertReviewerProfile.objects.filter(
                is_active_reviewer=True,
            ).select_related("user")
        )

        if len(reviewers) < k:
            raise CommandError(
                f"--k={k} but only {len(reviewers)} active "
                "reviewer(s) exist."
            )

        seed = options["seed"]

        if seed is None:
            seed = random.SystemRandom().randrange(
                0,
                2**31 - 1,
            )

        plan = self._build_plan(
            questions,
            reviewers,
            k,
            seed,
        )

        # Anything already assigned is skipped rather than attempted
        # again, so the command can be re-run on a partially-assigned
        # batch (e.g. after adding more questions to the same CSV)
        # without tripping the unique_reviewer_question_assignment
        # constraint.
        existing_pairs = set(
            ReviewAssignment.objects.filter(
                question__in=questions,
            ).values_list("reviewer_id", "question_id")
        )

        to_create = []
        already_existed = 0

        for reviewer, entries in plan.items():

            for question, display_order in entries:

                if (
                    reviewer.pk,
                    question.pk,
                ) in existing_pairs:

                    already_existed += 1
                    continue

                to_create.append(
                    ReviewAssignment(
                        reviewer=reviewer,
                        question=question,
                        display_order=display_order,
                    )
                )

        self._report(
            plan=plan,
            to_create=to_create,
            already_existed=already_existed,
            seed=seed,
            k=k,
            dry_run=options["dry_run"],
        )

        if options["dry_run"]:
            return

        with transaction.atomic():
            ReviewAssignment.objects.bulk_create(to_create)

    # -----------------------------------------------------
    # Reporting
    # -----------------------------------------------------

    def _report(
        self,
        plan,
        to_create,
        already_existed,
        seed,
        k,
        dry_run,
    ):

        if dry_run:

            self.stdout.write(
                "--- DRY RUN: nothing will be written ---\n"
            )

            for reviewer, entries in plan.items():

                label = (
                    reviewer.user.get_full_name()
                    or reviewer.user.username
                )

                self.stdout.write(f"\n{label}:")

                for question, display_order in entries:

                    self.stdout.write(
                        f"  {display_order:>3}. "
                        f"{question.blind_id}"
                    )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Assignments {'that would be ' if dry_run else ''}"
                f"created: {len(to_create)}"
            )
        )

        if already_existed:

            self.stdout.write(
                self.style.WARNING(
                    f"Already existed (skipped): {already_existed}"
                )
            )

        self.stdout.write("\nPer-reviewer question count:")

        counts = sorted(
            (
                (
                    reviewer.user.get_full_name()
                    or reviewer.user.username,
                    len(entries),
                )
                for reviewer, entries in plan.items()
            ),
            key=lambda row: row[0],
        )

        for label, count in counts:
            self.stdout.write(f"  {label}: {count}")

        if counts:

            values = [count for _, count in counts]

            self.stdout.write(
                f"\n  (min={min(values)}, max={max(values)}, "
                f"spread={max(values) - min(values)})"
            )

        self.stdout.write(f"\nk (reviewers per question): {k}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed used: {seed}  "
                f"(pass --seed={seed} to reproduce this exact plan)"
            )
        )
