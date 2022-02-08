from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email = 'email@email.com', password = 'password'):
    """Generates a sample user"""
    return get_user_model().objects.create_user(email, password)

class RecipeModelTests(TestCase):
    """Contains tests for the recipe model"""

    def test_recipe_to_string(self):
        """Tests the to string method of recipe"""

        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title = 'Steak and mushroom sauce',
            time_minutes=5,
            price = 19.99
        )

        self.assertEqual(str(recipe), recipe.title)