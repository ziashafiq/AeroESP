import random
from collections import defaultdict

from django.shortcuts import render

from .models import Question


def build_balanced_test():
    """
    Build a balanced 9-question assessment.

    Blueprint:
        3 language skills × 3 aerospace domains
        = 9 questions
    """

    selected_questions = []

    skills = [
        Question.Skill.VOCABULARY,
        Question.Skill.GRAMMAR,
        Question.Skill.READING,
    ]

    domains = [
        Question.Domain.AERODYNAMICS,
        Question.Domain.FLIGHT_DYNAMICS,
        Question.Domain.PROPULSION,
    ]

    for skill in skills:
        for domain in domains:

            candidates = list(
                Question.objects.filter(
                    track=Question.Track.AEROSPACE_ESP,
                    skill=skill,
                    aerospace_domain=domain,
                )
            )

            if candidates:
                selected_question = random.choice(candidates)
                selected_questions.append(selected_question)

    random.shuffle(selected_questions)

    return selected_questions


def quiz(request):

    # ---------------------------------------------------------
    # START A NEW ASSESSMENT
    # ---------------------------------------------------------

    if request.method == "GET":

        questions = build_balanced_test()

        # Save the selected question IDs so the submitted test
        # is graded using exactly the same questions.
        request.session["quiz_question_ids"] = [
            question.id
            for question in questions
        ]

        return render(
            request,
            "assessment/quiz.html",
            {
                "questions": questions,
            },
        )

    # ---------------------------------------------------------
    # GRADE THE SUBMITTED ASSESSMENT
    # ---------------------------------------------------------

    question_ids = request.session.get(
        "quiz_question_ids",
        [],
    )

    question_map = Question.objects.in_bulk(
        question_ids
    )

    questions = [
        question_map[question_id]
        for question_id in question_ids
        if question_id in question_map
    ]

    total_questions = len(questions)
    correct_count = 0

    skill_stats = defaultdict(
        lambda: {
            "correct": 0,
            "total": 0,
        }
    )

    domain_stats = defaultdict(
        lambda: {
            "correct": 0,
            "total": 0,
        }
    )

    detailed_results = []

    for question in questions:

        selected_answer = request.POST.get(
            f"question_{question.id}"
        )

        is_correct = (
            selected_answer
            == question.correct_answer
        )

        if is_correct:
            correct_count += 1

        skill_name = question.get_skill_display()

        domain_name = (
            question.get_aerospace_domain_display()
        )

        skill_stats[skill_name]["total"] += 1
        domain_stats[domain_name]["total"] += 1

        if is_correct:
            skill_stats[skill_name]["correct"] += 1
            domain_stats[domain_name]["correct"] += 1

        detailed_results.append(
            {
                "question": question,
                "selected_answer": selected_answer,
                "is_correct": is_correct,
            }
        )

    # ---------------------------------------------------------
    # OVERALL SCORE
    # ---------------------------------------------------------

    if total_questions > 0:
        overall_percentage = round(
            (correct_count / total_questions) * 100
        )
    else:
        overall_percentage = 0

    # ---------------------------------------------------------
    # LANGUAGE SKILL ANALYSIS
    # ---------------------------------------------------------

    skill_results = []

    for name, values in skill_stats.items():

        percentage = round(
            (
                values["correct"]
                / values["total"]
            )
            * 100
        )

        skill_results.append(
            {
                "name": name,
                "correct": values["correct"],
                "total": values["total"],
                "percentage": percentage,
            }
        )

    # ---------------------------------------------------------
    # AEROSPACE DOMAIN ANALYSIS
    # ---------------------------------------------------------

    domain_results = []

    for name, values in domain_stats.items():

        percentage = round(
            (
                values["correct"]
                / values["total"]
            )
            * 100
        )

        domain_results.append(
            {
                "name": name,
                "correct": values["correct"],
                "total": values["total"],
                "percentage": percentage,
            }
        )

    context = {
        "total_questions": total_questions,
        "correct_count": correct_count,
        "overall_percentage": overall_percentage,
        "skill_results": skill_results,
        "domain_results": domain_results,
        "detailed_results": detailed_results,
    }

    return render(
        request,
        "assessment/result.html",
        context,
    )