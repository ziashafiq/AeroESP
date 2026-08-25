def build_quality_advice(
    quality_report,
):

    if not quality_report:
        return {
            "decision": "UNKNOWN",
            "message": "No quality evaluation available.",
        }

    score = quality_report.get(
        "score",
        0,
    )

    warnings = quality_report.get(
        "warnings",
        [],
    )

    if score >= 80:

        decision = "READY_FOR_REVIEW"

        message = (
            "Generated question passed "
            "quality checks and is ready "
            "for teacher review."
        )

    elif score >= 60:

        decision = "NEEDS_REVIEW"

        message = (
            "Generated question requires "
            "teacher review before approval."
        )

    else:

        decision = "NEEDS_IMPROVEMENT"

        message = (
            "Generated question quality is "
            "below acceptable level."
        )

    return {
        "decision": decision,
        "message": message,
        "score": score,
        "warnings": warnings,
    }