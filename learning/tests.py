from django.test import SimpleTestCase

from learning.models import LearningCourse
from learning.views import (
    _course_level_from_cefr,
)


class PlacementLevelMappingTests(
    SimpleTestCase
):

    def test_cefr_course_level_mapping(
        self,
    ):

        cases = {
            "A1": (
                LearningCourse
                .Level
                .BEGINNER
            ),
            "A2": (
                LearningCourse
                .Level
                .ELEMENTARY
            ),
            "B1": (
                LearningCourse
                .Level
                .INTERMEDIATE
            ),
            "B2": (
                LearningCourse
                .Level
                .UPPER_INTERMEDIATE
            ),
            "C1": (
                LearningCourse
                .Level
                .ADVANCED
            ),
            "C2": (
                LearningCourse
                .Level
                .ADVANCED
            ),
        }

        for cefr, expected in cases.items():

            with self.subTest(
                cefr=cefr
            ):

                self.assertEqual(
                    _course_level_from_cefr(
                        cefr
                    ),
                    expected,
                )

    def test_unknown_cefr_returns_blank(
        self,
    ):

        self.assertEqual(
            _course_level_from_cefr(
                "UNKNOWN"
            ),
            "",
        )