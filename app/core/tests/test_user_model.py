from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with email is successful"""
        
        email = 'test@email.com'
        password = 'pass123'

        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normalized(self):
        """Test the that a new users email is normalized"""
        
        email = 'test@SoMeVaLue.com'

        user = get_user_model().objects.create_user(
            email = email,
            password = 'pass'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email"""
        
        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user(
                email = None,
                password = "pass"
            )

    def test_create_new_superUser(self):
        """Test creating a new super user"""

        user = get_user_model().objects.create_superUser(
            'test@email.com',
            'pass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

