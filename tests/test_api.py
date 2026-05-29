from django.test import SimpleTestCase

from api import get_open_restaurants, is_restaurant_open


class RestaurantParsingTests(SimpleTestCase):
    def test_regular_hours_match(self):
        self.assertTrue(
            is_restaurant_open(
                "Mon-Sun 11:00 am - 10 pm",
                "2024-01-15 12:00:00",
            )
        )

    def test_day_specific_schedule(self):
        self.assertTrue(
            is_restaurant_open(
                "Mon-Fri 11 am - 10 pm / Sat-Sun 5 pm - 10 pm",
                "2024-01-13 18:00:00",
            )
        )
        self.assertFalse(
            is_restaurant_open(
                "Mon-Fri 11 am - 10 pm / Sat-Sun 5 pm - 10 pm",
                "2024-01-13 10:00:00",
            )
        )

    def test_overnight_hours(self):
        self.assertTrue(
            is_restaurant_open(
                "Mon-Sun 11 am - 4 am",
                "2024-01-15 01:00:00",
            )
        )
        self.assertFalse(
            is_restaurant_open(
                "Mon-Sun 11 am - 4 am",
                "2024-01-15 05:00:00",
            )
        )

    def test_multiple_day_blocks(self):
        self.assertTrue(
            is_restaurant_open(
                "Mon-Fri, Sat 11 am - 12 pm / Sun 11 am - 10 pm",
                "2024-01-13 11:30:00",
            )
        )
        self.assertTrue(
            is_restaurant_open(
                "Mon-Fri, Sat 11 am - 12 pm / Sun 11 am - 10 pm",
                "2024-01-14 11:30:00",
            )
        )

    def test_get_open_restaurants_from_csv(self):
        open_restaurants = get_open_restaurants("2024-01-15 12:00:00")
        self.assertIn("The Cowfish Sushi Burger Bar", open_restaurants)
        self.assertIn("Seoul 116", open_restaurants)
        self.assertNotIn("Bonchon", open_restaurants)
