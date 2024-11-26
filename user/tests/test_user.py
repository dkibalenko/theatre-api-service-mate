from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from user.serializers import UserSerializer, AuthTokenSerializer


class UserTests(TestCase):
    def test_create_user_without_email_should_raise_value_error(self):
        with self.assertRaises(ValueError) as cm:
            get_user_model().objects.create_user(
                email=None,
                password="testpassword"
            )

        self.assertEqual(str(cm.exception), "The given email must be set")

    def test_create_superuser_with_invalid_is_staff_raises_value_error(self):
        with self.assertRaises(ValueError) as cm:
            get_user_model().objects.create_superuser(
                email="test@test",
                password="testpassword",
                is_staff=False
            )

        self.assertEqual(
            str(cm.exception),
            "Superuser must have is_staff=True."
        )

    def test_create_superuser_with_invalid_is_superuser_raise_valueerror(self):
        with self.assertRaises(ValueError) as cm:
            get_user_model().objects.create_superuser(
                email="test@test",
                password="testpassword",
                is_superuser=False
            )

        self.assertEqual(
            str(cm.exception),
            "Superuser must have is_superuser=True."
        )


class UserSerializerTests(APITestCase):
    def test_create_user(self):
        payload = {
            "email": "test@test.com",
            "password": "testpassword"
        }
        serializer = UserSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", serializer.data)
        self.assertEqual(user.email, payload["email"])

    def test_update_user(self):
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword"
        )
        payload = {
            "email": "test2@test.com",
            "password": "testpassword2"
        }
        serializer = UserSerializer(
            instance=user,
            data=payload,
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertTrue(updated_user.check_password(payload["password"]))
        self.assertEqual(updated_user.email, payload["email"])
