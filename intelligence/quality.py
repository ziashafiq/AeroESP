def evaluate_question_quality(
    *,
    result,
    track,
    skill,
    difficulty,
):
    warnings = []

    required = [
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "explanation",
    ]

    completeness = all(
        result.get(field)
        for field in required
    )

    options = [
        result.get("option_a"),
        result.get("option_b"),
        result.get("option_c"),
        result.get("option_d"),
    ]

    options_quality = (
        len(set(options)) == 4
        if all(options)
        else False
    )

    explanation_quality = bool(
        result.get("explanation")
        and len(result["explanation"].strip()) > 20
    )

    score = 100

    if not completeness:
        score -= 30
        warnings.append(
            "Missing required fields"
        )

    if not options_quality:
        score -= 25
        warnings.append(
            "Options are not unique"
        )

    if not explanation_quality:
        score -= 15
        warnings.append(
            "Explanation is weak"
        )

    if score >= 80:
        status = "GOOD"
    elif score >= 60:
        status = "REVIEW"
    else:
        status = "POOR"

    return {
        "score": score,
        "status": status,
        "checks": {
            "completeness": completeness,
            "options": options_quality,
            "explanation": explanation_quality,
        },
        "warnings": warnings,
    }