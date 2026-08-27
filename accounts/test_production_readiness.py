from django.test import TestCase
from django.urls import reverse


class ProductionReadinessTests(
    TestCase
):

    def test_liveness_endpoint(
        self,
    ):

        response = self.client.get(
            reverse(
                "health_live"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()[
                "status"
            ],
            "ok",
        )

    def test_readiness_endpoint(
        self,
    ):

        response = self.client.get(
            reverse(
                "health_ready"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()[
                "database"
            ],
            "ok",
        )

    def test_custom_404(
        self,
    ):

        response = self.client.get(
            (
                "/definitely-"
                "not-a-real-page/"
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertTemplateUsed(
            response,
            "404.html",
        )

    def test_password_reset_page(
        self,
    ):

        response = self.client.get(
            reverse(
                "password_reset"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )