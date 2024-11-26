from django.test import TestCase
from django.contrib.auth import get_user_model


class UserTests(TestCase):
    def test_create_user_without_email_should_raise_value_error(self):
        with self.assertRaises(ValueError) as cm:
            get_user_model().objects.create_user(
                email=None,
                password="testpassword"
            )

        self.assertEqual(str(cm.exception), "The given email must be set")
