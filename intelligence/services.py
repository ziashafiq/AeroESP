import json
import os
import time
from decimal import Decimal

from django.conf import settings
from django.db import models

from assessment.models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)

from learning.models import (
    LearnerError,
    LearningProgress,
    LearningProgram,
)

from .models import (
    LearnerInsightSnapshot,
    QuestionAISuggestion,
)

from .provider_registry import (
    get_provider_info,
)


AEROSPACE_KEYWORDS = {
    "aircraft",
    "aerospace",
    "aerodynamic",
    "aerodynamics",
    "airfoil",
    "wing",
    "lift",
    "drag",
    "thrust",
    "flight",
    "stability",
    "control",
    "propulsion",
    "turbine",
    "compressor",
    "engine",
    "fuselage",
    "satellite",
    "spacecraft",
    "orbit",
    "rocket",
    "mach",
    "reynolds",
}


GRAMMAR_KEYWORDS = {
    "grammar",
    "tense",
    "article",
    "preposition",
    "conditional",
    "passive",
    "modal",
    "relative clause",
    "gerund",
    "infinitive",
}


VOCABULARY_KEYWORDS = {
    "meaning",
    "synonym",
    "antonym",
    "word",
    "vocabulary",
    "definition",
    "collocation",
}


READING_KEYWORDS = {
    "passage",
    "according to the text",
    "according to the passage",
    "main idea",
    "paragraph",
    "author",
    "reading",
}


def _question_text(question):

    values = [
        question.question_text or "",
        question.option_a or "",
        question.option_b or "",
        question.option_c or "",
        question.option_d or "",
    ]

    return " ".join(
        values
    ).lower()


def _difficulty_value(question, level):

    field = question._meta.get_field(
        "difficulty"
    )

    choices = list(
        field.choices or []
    )

    if not choices:
        return level.upper()

    wanted = level.lower()

    for value, label in choices:

        label_text = str(
            label
        ).lower()

        value_text = str(
            value
        ).lower()

        if (
            wanted in label_text
            or wanted in value_text
        ):
            return value

    return choices[0][0]


def analyze_question(
    question,
    created_by=None,
):

    text = _question_text(
        question
    )

    aerospace_hits = sum(
        1
        for keyword in AEROSPACE_KEYWORDS
        if keyword in text
    )

    if aerospace_hits:

        suggested_track = (
            Question.Track
            .AEROSPACE_ESP
        )

    else:

        suggested_track = (
            Question.Track
            .GENERAL_ENGLISH
        )

    grammar_hits = sum(
        1
        for keyword in GRAMMAR_KEYWORDS
        if keyword in text
    )

    vocabulary_hits = sum(
        1
        for keyword in VOCABULARY_KEYWORDS
        if keyword in text
    )

    reading_hits = sum(
        1
        for keyword in READING_KEYWORDS
        if keyword in text
    )

    scores = {
        Question.Skill.GRAMMAR:
            grammar_hits,

        Question.Skill.VOCABULARY:
            vocabulary_hits,

        Question.Skill.READING:
            reading_hits,
    }

    suggested_skill = max(
        scores,
        key=scores.get,
    )

    if not max(scores.values()):

        suggested_skill = (
            question.skill
            or Question.Skill.VOCABULARY
        )

    text_length = len(
        question.question_text or ""
    )

    if text_length < 100:
        difficulty_level = "easy"

    elif text_length < 240:
        difficulty_level = "medium"

    else:
        difficulty_level = "hard"

    suggested_difficulty = (
        _difficulty_value(
            question,
            difficulty_level,
        )
    )

    suggested_domain = None
    suggested_topic = None

    if (
        suggested_track
        == Question.Track.AEROSPACE_ESP
    ):

        domains = (
            AerospaceDomain.objects
            .filter(is_active=True)
            .order_by("order", "name")
        )

        best_domain_score = 0

        for domain in domains:

            tokens = [
                domain.name.lower(),
            ]

            code = getattr(
                domain,
                "code",
                "",
            )

            if code:
                tokens.append(
                    str(code).lower()
                )

            score = sum(
                1
                for token in tokens
                if token
                and token in text
            )

            if score > best_domain_score:

                best_domain_score = score
                suggested_domain = domain

        if suggested_domain:

            topics = (
                AerospaceTopic.objects
                .filter(
                    domain=suggested_domain,
                )
                .order_by(
                    "order",
                    "name",
                )
            )

            best_topic_score = 0

            for topic in topics:

                name = (
                    topic.name
                    .lower()
                )

                score = (
                    1
                    if name in text
                    else 0
                )

                if score > best_topic_score:

                    best_topic_score = (
                        score
                    )

                    suggested_topic = (
                        topic
                    )

    evidence_hits = (
        aerospace_hits
        + grammar_hits
        + vocabulary_hits
        + reading_hits
    )

    confidence = min(
        Decimal("0.95"),
        Decimal("0.55")
        + Decimal(
            str(
                min(
                    evidence_hits,
                    8,
                )
                * 0.05
            )
        ),
    )

    rationale_parts = []

    if aerospace_hits:
        rationale_parts.append(
            f"{aerospace_hits} aerospace "
            f"keyword signals detected"
        )

    if grammar_hits:
        rationale_parts.append(
            f"{grammar_hits} grammar "
            f"signals detected"
        )

    if vocabulary_hits:
        rationale_parts.append(
            f"{vocabulary_hits} vocabulary "
            f"signals detected"
        )

    if reading_hits:
        rationale_parts.append(
            f"{reading_hits} reading "
            f"signals detected"
        )

    rationale_parts.append(
        f"Question length = "
        f"{text_length} characters"
    )

    suggestion = (
        QuestionAISuggestion.objects
        .create(
            question=question,
            suggested_track=(
                suggested_track
            ),
            suggested_skill=(
                suggested_skill
            ),
            suggested_difficulty=(
                suggested_difficulty
            ),
            suggested_domain=(
                suggested_domain
            ),
            suggested_topic=(
                suggested_topic
            ),
            confidence=confidence,
            rationale="; ".join(
                rationale_parts
            ),
            created_by=created_by,
            raw_output={
                "aerospace_hits":
                    aerospace_hits,
                "grammar_hits":
                    grammar_hits,
                "vocabulary_hits":
                    vocabulary_hits,
                "reading_hits":
                    reading_hits,
                "text_length":
                    text_length,
            },
        )
    )

    return suggestion


def build_learner_insight(
    student,
    scope="OVERALL",
):

    progress = (
        LearningProgress.objects
        .filter(student=student)
        .select_related(
            "learning_item",
            "learning_item__module",
            "learning_item__module__course",
            (
                "learning_item__module__"
                "course__program"
            ),
        )
    )

    errors = (
        LearnerError.objects
        .filter(
            student=student,
            resolved=False,
        )
    )

    if scope == "GENERAL":

        progress = progress.filter(
            learning_item__module__course__program__program_type=(
                LearningProgram
                .ProgramType
                .IELTS
            )
        )

        errors = errors.filter(
            is_general_english_error=True
        )

    elif scope == "AEROSPACE":

        progress = progress.filter(
            learning_item__module__course__program__program_type=(
                LearningProgram
                .ProgramType
                .AEROSPACE_ESP
            )
        )

        errors = errors.filter(
            is_esp_specific_error=True
        )

    progress_rows = list(
        progress
    )

    correct = sum(
        row.correct_count
        for row in progress_rows
    )

    incorrect = sum(
        row.incorrect_count
        for row in progress_rows
    )

    attempts = (
        correct + incorrect
    )

    accuracy = (
        correct
        / attempts
        * 100
        if attempts
        else 0
    )

    tracked = len(
        progress_rows
    )

    mastered = sum(
        1
        for row in progress_rows
        if row.status
        == LearningProgress
        .Status
        .MASTERED
    )

    mastery = (
        mastered
        / tracked
        * 100
        if tracked
        else 0
    )

    unresolved_errors = (
        errors.count()
    )

    # ------------------------------------------
    # Explainable risk score: 0–100
    # ------------------------------------------

    risk = 0.0

    if attempts:
        risk += (
            100 - accuracy
        ) * 0.45

    if tracked:
        risk += (
            100 - mastery
        ) * 0.30

    risk += min(
        unresolved_errors * 4,
        25,
    )

    risk = min(
        round(risk, 2),
        100,
    )

    if risk < 25:
        risk_band = "LOW"

    elif risk < 50:
        risk_band = "MODERATE"

    elif risk < 75:
        risk_band = "HIGH"

    else:
        risk_band = "CRITICAL"

    error_categories = list(
        errors
        .values("category")
        .annotate(
            total=models.Count("id")
        )
        .order_by("-total")[:5]
    )

    recommendations = []

    if accuracy < 60 and attempts:
        recommendations.append(
            "Prioritize corrective practice "
            "before introducing harder items."
        )

    if mastery < 50 and tracked:
        recommendations.append(
            "Increase spaced review of "
            "non-mastered learning items."
        )

    if unresolved_errors:

        recommendations.append(
            "Review unresolved learner errors "
            "and target the most frequent "
            "error categories."
        )

    for category in error_categories[:3]:

        recommendations.append(
            "Target additional practice for "
            f"{category['category']}."
        )

    if not recommendations:

        recommendations.append(
            "Continue the current adaptive "
            "practice and review schedule."
        )

    summary = (
        f"Accuracy {accuracy:.1f}%, "
        f"mastery {mastery:.1f}%, "
        f"{unresolved_errors} unresolved "
        f"errors. Risk level: "
        f"{risk_band}."
    )

    snapshot = (
        LearnerInsightSnapshot.objects
        .create(
            student=student,
            scope=scope,
            risk_score=risk,
            risk_band=risk_band,
            summary=summary,
            recommendations=(
                recommendations
            ),
            evidence={
                "correct": correct,
                "incorrect": incorrect,
                "attempts": attempts,
                "accuracy": round(
                    accuracy,
                    2,
                ),
                "tracked": tracked,
                "mastered": mastered,
                "mastery": round(
                    mastery,
                    2,
                ),
                "unresolved_errors": (
                    unresolved_errors
                ),
                "top_error_categories": (
                    error_categories
                ),
            },
        )
    )

    return snapshot


# =========================================================
# Helper: parse JSON from LLM responses (with markdown)
# =========================================================

def _parse_generated_json(
    content,
):

    content = (
        content
        or ""
    ).strip()

    if content.startswith("```"):

        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        content = "\n".join(
            lines
        ).strip()

    return json.loads(
        content
    )


# =========================================================
# Question Generator Framework
# =========================================================

class BaseQuestionGenerator:

    provider_name = "BASE"

    def generate(
        self,
        *,
        track,
        skill,
        difficulty,
        domain=None,
        topic=None,
        theme="",
        teacher_instructions="",
        api_key=None,
        model_name=None,
    ):
        raise NotImplementedError


class BaselineQuestionGenerator(
    BaseQuestionGenerator
):

    provider_name = "BASELINE_V1"

    def generate(
        self,
        *,
        track,
        skill,
        difficulty,
        domain=None,
        topic=None,
        theme="",
        teacher_instructions="",
        api_key=None,
        model_name=None,
    ):

        start_time = time.perf_counter()

        subject = (
            theme.strip()
            if theme
            else ""
        )

        if not subject and topic:
            subject = topic.name

        if not subject and domain:
            subject = domain.name

        if not subject:
            subject = "English usage"

        if (
            track
            == Question.Track.AEROSPACE_ESP
        ):

            question_text = (
                "Which statement best describes "
                f"the technical meaning of "
                f"'{subject}' in an aerospace "
                "engineering context?"
            )

            option_a = (
                f"A technically appropriate "
                f"description of {subject}."
            )

            option_b = (
                "A statement unrelated to the "
                "engineering concept."
            )

            option_c = (
                "A grammatically possible but "
                "technically incorrect statement."
            )

            option_d = (
                "A definition from an unrelated "
                "discipline."
            )

            explanation = (
                f"Option A is the intended "
                f"technical interpretation of "
                f"{subject}. This baseline draft "
                f"must be reviewed and edited by "
                f"the teacher before use."
            )

        else:

            question_text = (
                "Which option best matches the "
                f"intended English usage related "
                f"to '{subject}'?"
            )

            option_a = (
                "The contextually appropriate "
                "English usage."
            )

            option_b = (
                "An unrelated usage."
            )

            option_c = (
                "A grammatically inappropriate "
                "usage."
            )

            option_d = (
                "A semantically unrelated usage."
            )

            explanation = (
                "Option A is the intended answer. "
                "This baseline item is generated "
                "only to exercise the AI-assisted "
                "draft workflow and requires "
                "teacher review."
            )

        latency_ms = int(
            (
                time.perf_counter()
                - start_time
            )
            * 1000
        )

        return {
            "question_text": question_text,
            "option_a": option_a,
            "option_b": option_b,
            "option_c": option_c,
            "option_d": option_d,
            "correct_answer": "A",
            "explanation": explanation,
            "provider": self.provider_name,
            "metadata": {
                "model": "baseline-v1",
                "provider": self.provider_name,
                "api_family": "local",
                "prompt_version": (
                    "QUESTION_GENERATION_V1"
                ),
                "latency_ms": latency_ms,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "request_id": "",
                "track": track,
                "skill": skill,
                "difficulty": difficulty,
                "theme": subject,
                "teacher_instructions": (
                    teacher_instructions
                ),
            },
        }


class QuestionGenerationError(
    RuntimeError
):
    pass


class OpenAIQuestionGenerator(
    BaseQuestionGenerator
):

    provider_name = (
        "OPENAI_RESPONSES_V1"
    )

    def __init__(self):

        self.model = getattr(
            settings,
            "AEROESP_OPENAI_MODEL",
            "gpt-5.6-luna",
        )

        self.timeout = getattr(
            settings,
            "AEROESP_OPENAI_TIMEOUT",
            45,
        )

    def _validate_result(
        self,
        data,
    ):

        required = [
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "explanation",
        ]

        for field in required:

            value = data.get(
                field
            )

            if (
                not isinstance(
                    value,
                    str,
                )
                or not value.strip()
            ):
                raise QuestionGenerationError(
                    (
                        "Generated field "
                        f"'{field}' is invalid."
                    )
                )

        if (
            data["correct_answer"]
            not in {
                "A",
                "B",
                "C",
                "D",
            }
        ):
            raise QuestionGenerationError(
                (
                    "Generated correct answer "
                    "must be A, B, C, or D."
                )
            )

        options = [
            data["option_a"].strip(),
            data["option_b"].strip(),
            data["option_c"].strip(),
            data["option_d"].strip(),
        ]

        if len(set(options)) != 4:
            raise QuestionGenerationError(
                (
                    "Generated answer options "
                    "must be unique."
                )
            )

        for option in options:

            if len(option) > 500:
                raise QuestionGenerationError(
                    (
                        "A generated option "
                        "exceeded the Question "
                        "Bank length limit."
                    )
                )

    def generate(
        self,
        *,
        track,
        skill,
        difficulty,
        domain=None,
        topic=None,
        theme="",
        teacher_instructions="",
        api_key=None,
        model_name=None,
    ):

        effective_api_key = (
            api_key.strip()
            if api_key
            else os.getenv(
                "OPENAI_API_KEY",
                "",
            ).strip()
        )

        if not effective_api_key:
            raise QuestionGenerationError(
                (
                    "OPENAI_API_KEY is not "
                    "configured and no API key "
                    "was provided."
                )
            )

        effective_model = (
            model_name.strip()
            if model_name
            else self.model
        )

        domain_name = (
            domain.name
            if domain
            else "general aerospace"
        )

        topic_name = (
            topic.name
            if topic
            else ""
        )

        theme_text = (
            theme.strip()
            or topic_name
            or domain_name
        )

        prompt = (
            "Generate one high-quality "
            "multiple-choice educational item. "
            f"Track: {track}. "
            f"Skill: {skill}. "
            f"Difficulty: {difficulty}. "
            f"Domain: {domain_name}. "
            f"Topic: {theme_text}. "
            "Teacher instructions: "
            f"{teacher_instructions or 'None'}. "
            "Return JSON only with exactly these "
            "keys: question_text, option_a, "
            "option_b, option_c, option_d, "
            "correct_answer, explanation. "
            "correct_answer must be one of "
            "A, B, C, or D."
        )

        try:

            from openai import OpenAI

            client = OpenAI(
                api_key=effective_api_key,
                timeout=self.timeout,
            )

            start_time = (
                time.perf_counter()
            )

            response = (
                client.responses.create(
                    model=effective_model,
                    instructions=(
                        "You are an expert "
                        "educational item writer "
                        "for Aerospace English, "
                        "ESP, and General English."
                    ),
                    input=prompt,
                )
            )

            latency_ms = int(
                (
                    time.perf_counter()
                    - start_time
                )
                * 1000
            )

            data = _parse_generated_json(
                response.output_text
            )

            self._validate_result(
                data
            )

            usage = getattr(
                response,
                "usage",
                None,
            )

            data["provider"] = (
                self.provider_name
            )

            data["metadata"] = {
                "model": effective_model,
                "provider": self.provider_name,
                "api_family": "responses",
                "request_id": (
                    getattr(
                        response,
                        "id",
                        "",
                    )
                    or ""
                ),
                "prompt_version": (
                    "QUESTION_GENERATION_V1"
                ),
                "latency_ms": latency_ms,
                "input_tokens": (
                    getattr(
                        usage,
                        "input_tokens",
                        0,
                    )
                    or 0
                ),
                "output_tokens": (
                    getattr(
                        usage,
                        "output_tokens",
                        0,
                    )
                    or 0
                ),
                "total_tokens": (
                    getattr(
                        usage,
                        "total_tokens",
                        0,
                    )
                    or 0
                ),
                "track": track,
                "skill": skill,
                "difficulty": difficulty,
                "domain": domain_name,
                "topic": topic_name,
                "theme": theme_text,
            }

            return data

        except QuestionGenerationError:
            raise

        except Exception as exc:
            raise QuestionGenerationError(
                (
                    "OpenAI generation failed: "
                    f"{exc}"
                )
            ) from exc


class DeepSeekQuestionGenerator(
    OpenAIQuestionGenerator
):

    provider_name = "DEEPSEEK_V1"

    def __init__(self):

        self.model = getattr(
            settings,
            "AEROESP_DEEPSEEK_MODEL",
            "deepseek-chat",
        )

        self.timeout = getattr(
            settings,
            "AEROESP_OPENAI_TIMEOUT",
            45,
        )

        self.base_url = (
            "https://api.deepseek.com"
        )

    def generate(
        self,
        *,
        track,
        skill,
        difficulty,
        domain=None,
        topic=None,
        theme="",
        teacher_instructions="",
        api_key=None,
        model_name=None,
    ):

        effective_api_key = (
            api_key.strip()
            if api_key
            else os.getenv(
                "DEEPSEEK_API_KEY",
                "",
            ).strip()
        )

        if not effective_api_key:
            raise QuestionGenerationError(
                "DeepSeek API key is missing."
            )

        effective_model = (
            model_name.strip()
            if model_name
            else self.model
        )

        domain_name = (
            domain.name
            if domain
            else "general aerospace"
        )

        topic_name = (
            topic.name
            if topic
            else ""
        )

        theme_text = (
            theme.strip()
            or topic_name
            or domain_name
        )

        prompt = (
            "Generate one high-quality "
            "multiple-choice educational item. "
            f"Track: {track}. "
            f"Skill: {skill}. "
            f"Difficulty: {difficulty}. "
            f"Domain: {domain_name}. "
            f"Topic: {theme_text}. "
            "Teacher instructions: "
            f"{teacher_instructions or 'None'}. "
            "Return raw JSON only with exactly "
            "these keys: question_text, "
            "option_a, option_b, option_c, "
            "option_d, correct_answer, "
            "explanation. correct_answer must "
            "be A, B, C, or D."
        )

        try:

            from openai import OpenAI

            client = OpenAI(
                api_key=effective_api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )

            start_time = (
                time.perf_counter()
            )

            response = (
                client.chat.completions.create(
                    model=effective_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert "
                                "educational item "
                                "writer for Aerospace "
                                "English, ESP, and "
                                "General English."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )
            )

            latency_ms = int(
                (
                    time.perf_counter()
                    - start_time
                )
                * 1000
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            data = _parse_generated_json(
                content
            )

            self._validate_result(
                data
            )

            usage = getattr(
                response,
                "usage",
                None,
            )

            data["provider"] = (
                self.provider_name
            )

            data["metadata"] = {
                "model": effective_model,
                "provider": self.provider_name,
                "api_family": (
                    "chat.completions"
                ),
                "request_id": (
                    getattr(
                        response,
                        "id",
                        "",
                    )
                    or ""
                ),
                "prompt_version": (
                    "QUESTION_GENERATION_V1"
                ),
                "latency_ms": latency_ms,
                "input_tokens": (
                    getattr(
                        usage,
                        "prompt_tokens",
                        0,
                    )
                    or 0
                ),
                "output_tokens": (
                    getattr(
                        usage,
                        "completion_tokens",
                        0,
                    )
                    or 0
                ),
                "total_tokens": (
                    getattr(
                        usage,
                        "total_tokens",
                        0,
                    )
                    or 0
                ),
                "track": track,
                "skill": skill,
                "difficulty": difficulty,
                "domain": domain_name,
                "topic": topic_name,
                "theme": theme_text,
            }

            return data

        except QuestionGenerationError:
            raise

        except Exception as exc:
            raise QuestionGenerationError(
                (
                    "DeepSeek generation failed: "
                    f"{exc}"
                )
            ) from exc


class GeminiQuestionGenerator(
    BaseQuestionGenerator
):

    provider_name = "GEMINI_V1"

    def generate(
        self,
        *,
        track,
        skill,
        difficulty,
        domain=None,
        topic=None,
        theme="",
        teacher_instructions="",
        api_key=None,
        model_name=None,
    ):

        raise QuestionGenerationError(
            (
                "Gemini provider is not enabled "
                "in this beta."
            )
        )


# =========================================================
# Generator Factory
# =========================================================

def get_question_generator(
    provider_name=None,
):

    if not provider_name:

        provider_name = getattr(
            settings,
            "AEROESP_AI_PROVIDER",
            "BASELINE_V1",
        )

    provider_info = get_provider_info(
        provider_name
    )

    if not provider_info:
        raise QuestionGenerationError(
            (
                "Unknown question generation "
                f"provider: {provider_name}"
            )
        )

    if (
        provider_name
        == "BASELINE_V1"
    ):
        return (
            BaselineQuestionGenerator()
        )

    if (
        provider_name
        == "OPENAI_RESPONSES_V1"
    ):
        return (
            OpenAIQuestionGenerator()
        )

    if (
        provider_name
        == "DEEPSEEK_V1"
    ):
        return (
            DeepSeekQuestionGenerator()
        )

    if (
        provider_name
        == "GEMINI_V1"
    ):
        return (
            GeminiQuestionGenerator()
        )

    raise QuestionGenerationError(
        (
            "Unknown question generation "
            f"provider: {provider_name}"
        )
    )