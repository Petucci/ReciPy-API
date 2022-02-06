from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

class PublicTagsApiTests(TestCase):
    """Test the publicly available API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that you must be logged in"""

        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)        
    
class PrivateTagsApiTests(TestCase):
    """Test the authorized user API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'email@email.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""

        Tag.objects.create(user = self.user, name='Vegan')
        Tag.objects.create(user = self.user, name='Desert')

        response = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_users_tags(self):
        """Test that only users tags are returned"""

        newUser = get_user_model().objects.create_user(
            'new@new.com',
            'newPassword'
        )

        Tag.objects.create(user = self.user, name='Vegan')
        Tag.objects.create(user = newUser, name='Desert')

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Vegan')

    def test_create_tag(self):
        """Tests that a tag is successfully created"""

        payload = {'name': 'Test tag'}
        response = self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user = self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_invalid_tag(self):
        """Tests for validation errors"""

        payload = {
            'name': ''
        }

        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)