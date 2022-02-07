from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientApiTests(TestCase):
    """Contains tests for the public api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required"""

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientApiTests(TestCase):
    """Test that authorized users can access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'mail@mail.com',
            'MyPassword123'
        )

        self.client.force_authenticate(self.user)

    def test_get_ingredients(self):
        """Tests that ingredients are retrieved"""

        Ingredient.objects.create(name='Sugar', user=self.user)
        Ingredient.objects.create(name='Salt', user=self.user)

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        createdIngredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(createdIngredients, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_only_my_ingredients_returned(self):
        """Test that only authenticated users ingredients are returned"""

        otherUser = get_user_model().objects.create_user(
            'second@mail.com',
            'NotMyPASS123'
        )

        Ingredient.objects.create(name='First',user=self.user)
        Ingredient.objects.create(name='Second',user=otherUser)

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'First')
        self.assertEqual(len(response.data), 1)

    def test_create_ingredient(self):
        """Test than an ingredient can be created"""

        payload = {'name': 'Salt'}
        response = self.client.post(INGREDIENTS_URL, payload)
        isInserted = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(isInserted)

    def test_create_ingredient_invalid(self):
        """test that creating invalid ingredients fails"""

        payload = {'name': ''}

        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
