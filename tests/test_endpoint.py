from django.test import Client, SimpleTestCase


class RestaurantEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_restaurant_endpoint_returns_open_names(self):
        response = self.client.get("/restaurants/", {"datetime": "2026-06-01 12:00:00"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["datetime"], "2026-06-01 12:00:00")
        self.assertIn("The Cowfish Sushi Burger Bar", payload["restaurants"])
        self.assertIn("Seoul 116", payload["restaurants"])

    def test_restaurant_endpoint_requires_datetime(self):
        response = self.client.get("/restaurants/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "datetime query parameter is required")
