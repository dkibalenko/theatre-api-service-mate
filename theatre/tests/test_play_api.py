import os
import tempfile

from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Play, Genre, Actor, Performance, TheatreHall
from theatre.serializers import PlayListSerializer, PlayDetailSerializer

PLAY_LIST_URL = reverse("theatre:play-list")
PERFORMANCE_LIST_URL = reverse("theatre:performance-list")


def sample_play(**params):
    defaults = {
        "title": "Test title play",
        "description": "Test play description"
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "Benny", "last_name": "Hill"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(
        name="Test theatre hall", rows=20, seats_in_row=20
    )

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "play": None,
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def image_upload_url(play_id):
    """Return URL for play image upload"""
    return reverse("theatre:play-upload-image", args=[play_id])

def detail_url(play_id):
    return reverse("theatre:play-detail", args=[play_id])


class PlayImageUploadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            password="password"
        )
        self.client.force_authenticate(self.user)
        self.play = sample_play()
        self.genre = sample_genre()
        self.actor = sample_actor()
        self.performance = sample_performance(play=self.play)

    def tearDown(self):
        self.play.image.delete()

    def test_upload_image_to_play(self):
        """Test uploading an image to play"""
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.play.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.play.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.play.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_play_list_should_not_work(self):
        url = PLAY_LIST_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(title="Title")
        self.assertFalse(play.image)

    def test_image_url_is_shown_on_play_detail(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.play.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_play_list(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(PLAY_LIST_URL)

        self.assertIn("image", res.data[0].keys())

    def test_image_url_is_shown_on_performance_detail(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(PERFORMANCE_LIST_URL)

        self.assertIn("play_image", res.data[0].keys())

class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_play_string_representation(self):
        play = sample_play()
        self.assertEqual(str(play), play.title)

    def test_retrieve_play_list_unauthenticated(self):
        """Test that authentication is required for retrieving play list"""
        res = self.client.get(PLAY_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_play_list_endpoint(self):
        """Test retrieving plays"""
        sample_play(title="Play 1")
        sample_play(title="Play 2")

        res = self.client.get(PLAY_LIST_URL)

        plays = Play.objects.all().order_by("title")
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_play_list_endpoint_with_filtered_by_title(self):
        """Test retrieving plays filtered by title"""
        sample_play(title="Play 1")
        sample_play(title="Play 2")

        res = self.client.get(PLAY_LIST_URL, data={"title": "Play 1"})

        plays = Play.objects.filter(title="Play 1")
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_play_list_endpoint_with_filtered_by_genre(self):
        """Test retrieving movies filtered by genre"""
        sample_play(title="Play 1")
        sample_play(title="Play 2")
        sample_play(title="Play 3")

        res = self.client.get(PLAY_LIST_URL, data={"genres": 1})

        plays = Play.objects.filter(genres__id=1)
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_play_list_endpoint_with_filtered_by_actor(self):
        """Test retrieving plays filtered by actor"""
        sample_play(title="Play 1")
        sample_play(title="Play 2")
        sample_play(title="Play 3")

        res = self.client.get(PLAY_LIST_URL, data={"actors": 1})

        plays = Play.objects.filter(actors__id=1)
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_play_detail_endpoint(self):
        """Test retrieving play detail"""
        play = sample_play(title="Play 1")

        res = self.client.get(detail_url(play.id))

        serializer = PlayDetailSerializer(play)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_play_forbidden(self):
        """Test creating a play is forbidden"""
        payload = {
            "title": "Play 1",
            "description": "Test description 1"
        }
        res = self.client.post(PLAY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class AdminPlayApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="adminpassword",
            is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        """Test creating a play by admin"""
        genres = sample_genre()
        actors = sample_actor()
        payload = {
            "title": "Play 2",
            "description": "Test description 2",
            "genres": [genres.id],
            "actors": [actors.id],
        }
        res = self.client.post(PLAY_LIST_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        play = Play.objects.get(id=res.data["id"])
        for key in payload.keys():
            if key in ["genres", "actors"]:
                related_obj_ids = [
                    related_obj.id 
                    for related_obj 
                    in getattr(play, key).all()
                ]
                self.assertEqual(related_obj_ids, payload[key])
            else:
                self.assertEqual(getattr(play, key), payload[key])

    def test_update_play_forbidden(self):
        """Test updating a play is forbidden"""
        play = sample_play(title="Play 1")
        payload = {
            "title": "Play 2",
            "description": "Test description 2",
        }
        res = self.client.put(detail_url(play.id), payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_play_forbidden(self):
        """Test deleting a play is forbidden"""
        play = sample_play(title="Play 1")
        res = self.client.delete(detail_url(play.id))

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_actor_string_representation(self):
        actor = sample_actor(first_name="Benny", last_name="Hill")
        self.assertEqual(str(actor), f"{actor.first_name} {actor.last_name}")
        self.assertEqual(
            actor.full_name,
            f"{actor.first_name} {actor.last_name}"
        )

    def test_genre_string_representation(self):
        genre = sample_genre(name="Drama")
        self.assertEqual(str(genre), genre.name)
