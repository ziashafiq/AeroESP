from django import forms

from assessment.models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


class QuestionGenerationForm(forms.Form):

    provider = forms.ChoiceField(
        choices=[
            (
                "BASELINE_V1",
                "Explainable Baseline",
            ),
            (
                "OPENAI_RESPONSES_V1",
                "OpenAI LLM",
            ),
        ],
        initial="BASELINE_V1",
        label="Generation Provider",
    )

    track = forms.ChoiceField(
        choices=Question.Track.choices,
        label="Learning Track",
    )

    skill = forms.ChoiceField(
        choices=Question.Skill.choices,
        label="Language Skill",
    )

    difficulty = forms.ChoiceField(
        choices=Question.Difficulty.choices,
        label="Difficulty",
    )

    domain = forms.ModelChoiceField(
        queryset=AerospaceDomain.objects.none(),
        required=False,
        label="Aerospace Domain",
    )

    topic = forms.ModelChoiceField(
        queryset=AerospaceTopic.objects.none(),
        required=False,
        label="Aerospace Topic",
    )

    theme = forms.CharField(
        max_length=200,
        required=False,
        label="Topic / Theme",
    )

    teacher_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": (
                    "Optional instructions for "
                    "question generation..."
                ),
            }
        ),
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields["domain"].queryset = (
            AerospaceDomain.objects
            .filter(is_active=True)
            .order_by(
                "order",
                "name",
            )
        )

        topics = (
            AerospaceTopic.objects
            .filter(is_active=True)
            .order_by(
                "domain__order",
                "order",
                "name",
            )
        )

        selected_track = (
            self.data.get("track")
            if self.is_bound
            else None
        )

        selected_domain = (
            self.data.get("domain")
            if self.is_bound
            else None
        )

        if (
            selected_track
            == Question.Track.GENERAL_ENGLISH
        ):
            self.fields[
                "domain"
            ].queryset = (
                AerospaceDomain.objects.none()
            )

            topics = topics.none()

        elif selected_domain:

            topics = topics.filter(
                domain_id=selected_domain
            )

        else:

            topics = topics.none()

        self.fields[
            "topic"
        ].queryset = topics

    def clean(self):

        cleaned = super().clean()

        track = cleaned.get(
            "track"
        )

        domain = cleaned.get(
            "domain"
        )

        topic = cleaned.get(
            "topic"
        )

        if (
            track
            == Question.Track.AEROSPACE_ESP
            and domain is None
        ):
            self.add_error(
                "domain",
                (
                    "Aerospace Domain is "
                    "required for Aerospace ESP."
                ),
            )

        if (
            topic is not None
            and domain is not None
            and topic.domain_id
            != domain.pk
        ):
            self.add_error(
                "topic",
                (
                    "The selected topic does not "
                    "belong to the selected domain."
                ),
            )

        return cleaned