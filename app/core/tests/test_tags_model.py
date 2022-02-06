from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email = 'email@email.com', password = 'password'):
    """Generates a sample user"""
    return get_user_model().objects.create_user(email, password)


class TagModelTests(TestCase):
    """Contains tests for the tag model"""

    def test_tag_to_string(self):
        """Test the Tag to String conversion"""

        tag = models.Tag.objects.create(
            user = sample_user(),
            name = 'Vegan'
        )

        self.assertEqual(str(tag), tag.name);

    