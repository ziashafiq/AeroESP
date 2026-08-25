from django.db.models import Avg

from .models import (
    AIInteractionEvent,
    AIQualitySnapshot,
    AIPromptVersion,
    GeneratedQuestionDraft,
)


def build_prompt_evaluation():

    results = []


    prompts = AIPromptVersion.objects.all()


    for prompt in prompts:

        generation_events = (
            AIInteractionEvent.objects
            .filter(
                event_type="GENERATION_SUCCESS",
                draft__isnull=False,
            )
        )


        drafts = GeneratedQuestionDraft.objects.filter(
            id__in=
            generation_events.values_list(
                "draft_id",
                flat=True,
            )
        )


        snapshots = (
            AIQualitySnapshot.objects
            .filter(
                draft__in=drafts
            )
        )


        total = drafts.count()


        accepted = (
            snapshots
            .filter(
                quality_data__action="teacher_accept"
            )
            .count()
        )


        edited = (
            snapshots
            .filter(
                quality_data__action="teacher_edit"
            )
            .count()
        )


        rejected = (
            snapshots
            .filter(
                quality_data__action="teacher_reject"
            )
            .count()
        )


        reviewed = (
            accepted
            + edited
            + rejected
        )


        review_rate = 0

        if total:
            review_rate = round(
                reviewed / total * 100,
                2,
            )


        decision_acceptance_rate = 0

        if reviewed:
            decision_acceptance_rate = round(
                accepted / reviewed * 100,
                2,
            )


        average_quality = (
            snapshots
            .aggregate(
                avg=Avg("score")
            )
            ["avg"]
        )


        acceptance_rate = 0

        if total:
            acceptance_rate = round(
                accepted / total * 100,
                2,
            )


        if average_quality and average_quality >= 80:
            recommendation = "GOOD"

        elif average_quality and average_quality >= 60:
            recommendation = "REVIEW"

        else:
            recommendation = "POOR"


        results.append(
            {
                "version": prompt.version,
                "provider": prompt.provider,
                "generations": total,
                "average_quality": (
                    round(
                        average_quality,
                        2,
                    )
                    if average_quality
                    else 0
                ),
                "accepted": accepted,
                "edited": edited,
                "rejected": rejected,
                "acceptance_rate": acceptance_rate,
                "recommendation": recommendation,
                "reviewed": reviewed,
                "review_rate": review_rate,
                "decision_acceptance_rate": decision_acceptance_rate,
            }
        )


    return results