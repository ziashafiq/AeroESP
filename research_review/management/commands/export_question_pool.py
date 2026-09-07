import csv
import random
from collections import Counter, defaultdict

from django.core.management.base import BaseCommand, CommandError

from research_review.models import ResearchQuestion


# Accepted spellings for the columns in the two supplied CSVs. The
# files come from outside the project, so the header is matched
# case-insensitively and by a small set of aliases rather than assumed
# byte-for-byte.
ID_COLUMNS = ("question_id", "blind_id", "id")
SERVICE_COLUMNS = ("service", "provider", "model")
CONDITION_COLUMNS = ("condition", "mode", "variant")


# What create_review_assignments reads. It looks for a "blind_id"
# column and falls back to the first column, so a single-column file
# under this name works with it directly.
POOL_COLUMNS = ("blind_id",)


MANIFEST_COLUMNS = (
    "blind_id",
    "selection",
    "service",
    "condition",
    "experiment",
    "domain",
    "topic",
    "skill",
    "run_id",
    "provider",
    "displayed_model",
    "item_number",
    "target_cefr",
    "target_cognitive_level",
    "raw_preserved",
    "question_provenance",
    "existing_assignments",
)


class Command(BaseCommand):
    help = (
        "Build the 100-question review pool from the externally "
        "curated GOLD80 selection plus a seeded, balanced top-up "
        "drawn from the full V4 id map. Writes a blind_id-only CSV "
        "for create_review_assignments and a separate manifest "
        "carrying the SERVICE/CONDITION metadata."
    )

    # -----------------------------------------------------
    # Arguments
    # -----------------------------------------------------

    def add_arguments(self, parser):

        parser.add_argument(
            "--gold",
            dest="gold_path",
            default="AeroESP_GOLD80_INTERNAL_SELECTION.csv",
            help=(
                "CSV of the pre-selected GOLD80 questions. Needs a "
                "QUESTION_ID column (blind_id values)."
            ),
        )

        parser.add_argument(
            "--id-map",
            dest="id_map_path",
            default="AeroESP_V4_INTERNAL_ID_MAP.csv",
            help=(
                "CSV mapping every question to SERVICE and CONDITION. "
                "Needs QUESTION_ID, SERVICE and CONDITION columns."
            ),
        )

        parser.add_argument(
            "--output",
            dest="output_path",
            default="questions.csv",
            help=(
                "Where to write the reviewer-facing pool "
                "(blind_id only). Default: questions.csv"
            ),
        )

        parser.add_argument(
            "--manifest",
            dest="manifest_path",
            default="question_pool_manifest.csv",
            help=(
                "Where to write the researcher-facing manifest with "
                "full provenance. NEVER give this to a reviewer - it "
                "names the model behind each item. "
                "Default: question_pool_manifest.csv"
            ),
        )

        parser.add_argument(
            "--target",
            type=int,
            default=100,
            help="Total pool size (default: 100).",
        )

        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help=(
                "Seed for the top-up draw, so the same inputs always "
                "produce the same 20 extra questions (default: 42)."
            ),
        )

        parser.add_argument(
            "--allow-assigned",
            action="store_true",
            help=(
                "Permit questions that already have a ReviewAssignment "
                "into the top-up. Off by default: re-reviewing an item "
                "an earlier reviewer already saw contaminates the "
                "sample."
            ),
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report the selection without writing either file.",
        )

    # -----------------------------------------------------
    # CSV loading
    # -----------------------------------------------------

    def _resolve_column(self, fieldnames, candidates, path, label):
        """
        Find one of `candidates` among the header, case- and
        space-insensitively. Raises rather than guessing, because
        silently reading the wrong column would produce a plausible
        but wrong pool.
        """

        if not fieldnames:
            raise CommandError(f"{path} has no header row.")

        normalised = {
            (name or "").strip().lower(): name
            for name in fieldnames
        }

        for candidate in candidates:
            if candidate in normalised:
                return normalised[candidate]

        raise CommandError(
            f"{path}: could not find a {label} column. Looked for "
            f"{', '.join(candidates)}; the file has "
            f"{', '.join(repr(f) for f in fieldnames)}."
        )

    def _read_csv(self, path):

        try:
            # utf-8-sig: these files are produced elsewhere and a BOM
            # would otherwise end up glued to the first header name.
            with open(path, newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                return reader.fieldnames, list(reader)

        except OSError as error:
            raise CommandError(f"Could not read {path}: {error}")

    def _load_gold(self, path):

        fieldnames, rows = self._read_csv(path)

        column = self._resolve_column(
            fieldnames,
            ID_COLUMNS,
            path,
            "question id",
        )

        ordered = []
        seen = set()

        for row in rows:

            value = (row.get(column) or "").strip()

            if not value:
                continue

            if value in seen:
                continue

            seen.add(value)
            ordered.append(value)

        if not ordered:
            raise CommandError(f"{path}: no question ids found.")

        return ordered

    def _load_id_map(self, path):

        fieldnames, rows = self._read_csv(path)

        id_column = self._resolve_column(
            fieldnames, ID_COLUMNS, path, "question id"
        )
        service_column = self._resolve_column(
            fieldnames, SERVICE_COLUMNS, path, "service"
        )
        condition_column = self._resolve_column(
            fieldnames, CONDITION_COLUMNS, path, "condition"
        )

        mapping = {}

        for row in rows:

            value = (row.get(id_column) or "").strip()

            if not value:
                continue

            mapping[value] = {
                "service": (row.get(service_column) or "").strip(),
                "condition": (row.get(condition_column) or "").strip(),
            }

        if not mapping:
            raise CommandError(f"{path}: no question ids found.")

        return mapping

    # -----------------------------------------------------
    # Validation against the database
    # -----------------------------------------------------

    def _load_questions(self, blind_ids):
        """
        Fetch every referenced question in one query, with the run and
        experiment needed for the manifest, and report anything the
        database does not have.
        """

        questions = {
            question.blind_id: question
            for question in ResearchQuestion.objects.filter(
                blind_id__in=blind_ids,
            ).select_related(
                "run",
                "run__experiment",
            )
        }

        missing = [
            blind_id
            for blind_id in blind_ids
            if blind_id not in questions
        ]

        return questions, missing

    # -----------------------------------------------------
    # Balanced top-up
    # -----------------------------------------------------

    def _choose_top_up(
        self,
        needed,
        candidates,
        questions,
        id_map,
        gold_ids,
        seed,
    ):
        """
        Fill the remaining slots so the pool stays as even as the
        inputs allow across service and experiment.

        Rather than a flat random sample - which would drift the
        careful GOLD80 balance - this repeatedly picks from whichever
        (service, experiment) cell is currently least represented in
        the pool so far, breaking ties with a seeded shuffle. The
        result is deterministic for a given seed and set of inputs.
        """

        if needed <= 0:
            return []

        rng = random.Random(seed)

        def cell(blind_id):
            service = id_map.get(blind_id, {}).get("service", "")
            question = questions.get(blind_id)
            experiment = (
                question.run.experiment.source_id
                if question
                else ""
            )
            return (service, experiment)

        # Where the already-chosen GOLD80 sits.
        counts = Counter(cell(blind_id) for blind_id in gold_ids)

        by_cell = defaultdict(list)

        for blind_id in candidates:
            by_cell[cell(blind_id)].append(blind_id)

        # Shuffle inside each cell once, then draw from the front, so
        # the choice within a cell is seeded rather than alphabetical.
        for bucket in by_cell.values():
            bucket.sort()
            rng.shuffle(bucket)

        chosen = []

        while len(chosen) < needed:

            available = [
                key for key, bucket in by_cell.items() if bucket
            ]

            if not available:
                break

            # Least represented first; ties broken deterministically
            # by the cell key so a given seed always resolves the same
            # way.
            available.sort(key=lambda key: (counts[key], key))

            key = available[0]

            chosen.append(by_cell[key].pop())
            counts[key] += 1

        return chosen

    # -----------------------------------------------------
    # Entry point
    # -----------------------------------------------------

    def handle(self, *args, **options):

        gold_ids = self._load_gold(options["gold_path"])
        id_map = self._load_id_map(options["id_map_path"])

        target = options["target"]

        if target < len(gold_ids):
            raise CommandError(
                f"--target={target} is smaller than the "
                f"{len(gold_ids)} questions in the GOLD selection."
            )

        # --- everything the two files reference must exist in the DB
        referenced = list(
            dict.fromkeys(list(gold_ids) + list(id_map))
        )

        questions, missing = self._load_questions(referenced)

        if missing:
            raise CommandError(
                f"{len(missing)} id(s) in the CSVs have no matching "
                "ResearchQuestion.blind_id, so the files and this "
                "database disagree. First few: "
                + ", ".join(missing[:10])
            )

        gold_not_in_map = [
            blind_id
            for blind_id in gold_ids
            if blind_id not in id_map
        ]

        # --- assignment state, read once
        assigned_ids = set(
            ResearchQuestion.objects.filter(
                blind_id__in=referenced,
                assignments__isnull=False,
            )
            .values_list("blind_id", flat=True)
            .distinct()
        )

        gold_already_assigned = [
            blind_id
            for blind_id in gold_ids
            if blind_id in assigned_ids
        ]

        gold_not_raw = [
            blind_id
            for blind_id in gold_ids
            if not questions[blind_id].raw_preserved
        ]

        # --- top-up
        gold_set = set(gold_ids)

        candidates = [
            blind_id
            for blind_id in id_map
            if blind_id not in gold_set
            and (
                options["allow_assigned"]
                or blind_id not in assigned_ids
            )
        ]

        needed = target - len(gold_ids)

        top_up = self._choose_top_up(
            needed=needed,
            candidates=candidates,
            questions=questions,
            id_map=id_map,
            gold_ids=gold_ids,
            seed=options["seed"],
        )

        pool = list(gold_ids) + top_up

        self._report(
            gold_ids=gold_ids,
            top_up=top_up,
            needed=needed,
            candidates=candidates,
            pool=pool,
            questions=questions,
            id_map=id_map,
            assigned_ids=assigned_ids,
            gold_already_assigned=gold_already_assigned,
            gold_not_raw=gold_not_raw,
            gold_not_in_map=gold_not_in_map,
            options=options,
        )

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    "\nDRY RUN - no files written."
                )
            )
            return

        self._write_pool(
            options["output_path"],
            pool,
        )

        self._write_manifest(
            options["manifest_path"],
            gold_ids,
            top_up,
            questions,
            id_map,
            assigned_ids,
        )

    # -----------------------------------------------------
    # Output
    # -----------------------------------------------------

    def _write_pool(self, path, pool):

        try:
            with open(path, "w", newline="", encoding="utf-8") as handle:

                writer = csv.writer(handle)
                writer.writerow(POOL_COLUMNS)

                for blind_id in pool:
                    writer.writerow([blind_id])

        except OSError as error:
            raise CommandError(f"Could not write {path}: {error}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nWrote {len(pool)} blind_id(s) to {path}"
            )
        )

    def _write_manifest(
        self,
        path,
        gold_ids,
        top_up,
        questions,
        id_map,
        assigned_ids,
    ):

        try:
            with open(path, "w", newline="", encoding="utf-8") as handle:

                writer = csv.writer(handle)
                writer.writerow(MANIFEST_COLUMNS)

                for selection, blind_ids in (
                    ("GOLD80", gold_ids),
                    ("TOP_UP", top_up),
                ):

                    for blind_id in blind_ids:

                        question = questions[blind_id]
                        run = question.run
                        experiment = run.experiment
                        meta = id_map.get(blind_id, {})

                        writer.writerow([
                            blind_id,
                            selection,
                            meta.get("service", ""),
                            meta.get("condition", ""),
                            experiment.source_id,
                            experiment.domain,
                            experiment.topic,
                            question.skill,
                            run.run_id,
                            run.provider,
                            run.displayed_model,
                            question.item_number,
                            experiment.target_cefr,
                            experiment.target_cognitive_level,
                            question.raw_preserved,
                            question.question_provenance,
                            "yes" if blind_id in assigned_ids else "no",
                        ])

        except OSError as error:
            raise CommandError(f"Could not write {path}: {error}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote manifest for {len(gold_ids) + len(top_up)} "
                f"question(s) to {path}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "  The manifest names the model behind every item. "
                "It is for the researcher only - handing it to a "
                "reviewer breaks blinding."
            )
        )

    # -----------------------------------------------------
    # Reporting
    # -----------------------------------------------------

    def _report(
        self,
        gold_ids,
        top_up,
        needed,
        candidates,
        pool,
        questions,
        id_map,
        assigned_ids,
        gold_already_assigned,
        gold_not_raw,
        gold_not_in_map,
        options,
    ):

        w = self.stdout.write

        w("")
        w("=" * 62)
        w("GOLD selection")
        w("=" * 62)
        w(f"  questions read        : {len(gold_ids)}")
        w(f"  all present in the DB : yes")
        w(f"  raw_preserved=True    : "
          f"{len(gold_ids) - len(gold_not_raw)} / {len(gold_ids)}")

        if gold_not_raw:
            w(self.style.ERROR(
                "  NOT raw_preserved     : "
                + ", ".join(gold_not_raw)
            ))

        if gold_not_in_map:
            w(self.style.WARNING(
                f"  missing from id map   : {len(gold_not_in_map)} "
                "(no SERVICE/CONDITION for these): "
                + ", ".join(gold_not_in_map[:10])
            ))

        if gold_already_assigned:
            w(self.style.WARNING(
                f"  already assigned      : "
                f"{len(gold_already_assigned)} -> "
                + ", ".join(gold_already_assigned)
            ))
            w("    (kept in the pool; create_review_assignments "
              "skips pairs that already exist)")
        else:
            w("  already assigned      : none")

        w("")
        w("=" * 62)
        w(f"Top-up  (seed={options['seed']})")
        w("=" * 62)
        w(f"  slots to fill         : {needed}")
        w(f"  eligible candidates   : {len(candidates)}")
        w(f"  chosen                : {len(top_up)}")

        if len(top_up) < needed:
            w(self.style.ERROR(
                f"  SHORT BY {needed - len(top_up)} - not enough "
                "eligible candidates."
            ))

        if not options["allow_assigned"]:
            w(f"  excluded as already assigned: "
              f"{len(assigned_ids - set(gold_ids))}")

        if top_up:
            w("")
            w("  chosen ids:")
            for blind_id in top_up:
                meta = id_map.get(blind_id, {})
                question = questions[blind_id]
                w(f"    {blind_id}  {meta.get('service',''):18s} "
                  f"{meta.get('condition',''):22s} "
                  f"{question.run.experiment.source_id:6s} "
                  f"{question.skill}")

        w("")
        w("=" * 62)
        w(f"Resulting pool: {len(pool)} questions")
        w("=" * 62)

        for label, key in (
            ("service", lambda b: id_map.get(b, {}).get("service", "(none)")),
            ("condition", lambda b: id_map.get(b, {}).get("condition", "(none)")),
            ("experiment", lambda b: questions[b].run.experiment.source_id),
            ("skill", lambda b: questions[b].skill),
        ):

            w(f"\n  by {label}:")

            gold_counts = Counter(key(b) for b in gold_ids)
            pool_counts = Counter(key(b) for b in pool)

            for value, count in sorted(pool_counts.items()):
                w(f"    {str(value)[:34]:34s} {count:4d}   "
                  f"(gold {gold_counts.get(value, 0)}, "
                  f"+{count - gold_counts.get(value, 0)})")

        duplicates = [
            value
            for value, count in Counter(pool).items()
            if count > 1
        ]

        w("")
        if duplicates:
            w(self.style.ERROR(
                "  DUPLICATES in pool: " + ", ".join(duplicates)
            ))
        else:
            w("  no duplicate ids in the pool")
