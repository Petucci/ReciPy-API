from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email = 'email@email.com', password = 'password'):
    """Generates a sample user"""
    return get_user_model().objects.create_user(email, password)


class IngredientTests(TestCase):
    """Contains tests for the ingredients model"""

    def test_ingredient_str(self):
        """Test the to string method"""

        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)