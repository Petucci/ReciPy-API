import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return URL for image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def sample_tag(user, name='default'):
    """Create and return an sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='default ingredient'):
    """Create and return an sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def detail_url(recipe_id):
    """Return recipe detail url"""

    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **params):
    """Create and return an sample recipe"""

    defaults = {
        'title': 'default title',
        'time_minutes': 5,
        'price': 9.99
    }

    defaults.update(params)

    return Recipe.objects.create(
        user=user,
        **defaults
    )


class PublicRecipeApiTests(TestCase):
    """Contains tests for the public api"""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated(self):
        """Test that you must be logged in"""

        response = self.client.get(RECIPE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Contains test for the private api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'mail@mail.com',
            'myPassword123'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_recipes(self):
        """Tests that recipes are returned"""

        sample_recipe(self.user)
        sample_recipe(self.user)

        response = self.client.get(RECIPE_URL)
        insertedRecipes = Recipe.objects.all().order_by('id')
        serializedRecipes = RecipeSerializer(insertedRecipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializedRecipes.data)

    def test_return_only_users_recipes(self):
        """Test that it returns only current users recipes"""

        newUser = get_user_model().objects.create_user(
            'other@mail.com',
            'password123new'
        )

        sample_recipe(self.user)
        sample_recipe(newUser)

        response = self.client.get(RECIPE_URL)

        myRecipes = Recipe.objects.filter(user=self.user)
        serialized = RecipeSerializer(myRecipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(myRecipes), 1)
        self.assertEqual(response.data, serialized.data)

    def test_detail_recipe_view(self):
        """Test viewing an recipe in details"""

        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)

        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_test(self):
        """Basic create test"""

        payload = {
            'title': 'cheese cake',
            'time_minutes': 30,
            'price': 10.00
        }
        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        createdRecipe = Recipe.objects.get(id=response.data['id'])

        for key in payload.keys():
            self.assertEqual(getattr(createdRecipe, key), payload[key])

    def test_create_recipe_with_tag(self):
        """Test creating recipe with tags"""

        vegan_tag = sample_tag(user=self.user, name='vegan')
        desert_tag = sample_tag(user=self.user, name='desert')

        payload = {
            'title': 'cake',
            'time_minutes': 60,
            'price': 10.99,
            'tags': [vegan_tag.id, desert_tag.id]
        }

        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        createdRecipe = Recipe.objects.get(id=response.data['id'])

        tags = createdRecipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(vegan_tag, tags)
        self.assertIn(desert_tag, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""

        salt = sample_ingredient(user=self.user, name='salt')
        sugar = sample_ingredient(user=self.user, name='sugar')

        payload = {
            'title': 'custom',
            'time_minutes': 100,
            'price': 0.99,
            'ingredients': [sugar.id, salt.id]
        }

        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        createdRecipe = Recipe.objects.get(id=response.data['id'])

        ingredients = createdRecipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(sugar, ingredients)
        self.assertIn(salt, ingredients)

    def test_filter_recipes_by_tags(self):
        recipe1 = sample_recipe(user=self.user, title='recipe1')
        recipe2 = sample_recipe(user=self.user, title='recipe2')
        recipe3 = sample_recipe(user=self.user, title='recipe3')

        tag_vegan = sample_tag(user=self.user, name='vegan')
        tag_meat = sample_tag(user=self.user, name='meat')

        recipe1.tags.add(tag_vegan)
        recipe2.tags.add(tag_meat)

        response = self.client.get(RECIPE_URL,
                                   {'tags': f'{tag_vegan.id},{tag_meat.id}'}
                                   )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_recipes_by_ingredients(self):
        """Test returning recipes with specific ingredients"""

        recipe1 = sample_recipe(user=self.user, title='recipe1')
        recipe2 = sample_recipe(user=self.user, title='recipe2')
        recipe3 = sample_recipe(user=self.user, title='recipe3')

        salt = sample_ingredient(user=self.user, name='salt')
        sugar = sample_ingredient(user=self.user, name='sugar')

        recipe1.ingredients.add(salt)
        recipe2.ingredients.add(sugar)

        response = self.client.get(RECIPE_URL,
                                   {'ingredients': f'{salt.id},{sugar.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)


class RecipeImageUploadTests(TestCase):
    """Contains tests for images"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'mail@mail.com',
            'pass123123'
        )

        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""

        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            response = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))
