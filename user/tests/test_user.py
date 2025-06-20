from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import serializers

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


class AuthTokenSerializerTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword"
        )

    def test_auth_token_serializer_valid_credentials(self):
        serializer = AuthTokenSerializer(
            data={
                "email": "test@test.com",
                "password": "testpassword"
            }
        )
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)

    def test_auth_token_serializer_invalid_credentials(self):
        serializer = AuthTokenSerializer(
            data={
                "email": "test@test.com",
                "password": "wrongpassword"
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_auth_token_serializer_missing_email(self):
        serializer = AuthTokenSerializer(
            data={
                "password": "testpassword"
            }
        )
        self.assertFalse(serializer.is_valid())
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

        self.assertIn("email", serializer.errors)
        self.assertEqual(
            serializer.errors["email"][0],
            "This field is required."
        )

    def test_auth_token_serializer_missing_password(self):
        serializer = AuthTokenSerializer(
            data={
                "email": "test@test.com"
            }
        )
        self.assertFalse(serializer.is_valid())
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
            
        self.assertIn("password", serializer.errors)
        self.assertEqual(
            serializer.errors["password"][0],
            "This field is required."
        )

    def test_auth_token_serializer_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        serializer = AuthTokenSerializer(
            data={
                "email": "test@test.com",
                "password": "testpassword"
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
