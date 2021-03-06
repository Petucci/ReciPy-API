from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
ME_URL = reverse('user:me')
TOKEN_URL = reverse('user:token')

def create_user(**params):
    """Creates an user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Contains API tests for users (unauthenticated)"""

    def setUp(self):
        self.client = APIClient()
        self.generic_payload = {
        'email' : 'temporary@email.com',
        'password': 'MyPassword123!!!',
        'name': 'test name'
        }


    def test_create_valid_user(self):
        """Test creating user with valid payload"""
        response = self.client.post(CREATE_USER_URL, self.generic_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.get(**response.data).check_password(self.generic_payload['password']))
        self.assertNotIn('password', response.data)
        
    def test_user_exists(self):
        """test creating user that already exists fails"""
        
        create_user(**self.generic_payload)

        response = self.client.post(CREATE_USER_URL, self.generic_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that creating user with too short password fails"""

        payload = self.generic_payload
        payload['password'] = ''

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(exists)

    def test_create_token(self):
        """test that a token can be created"""

        create_user(**self.generic_payload)

        response = self.client.post(TOKEN_URL, self.generic_payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_create_token_invalid_credentials(self):
        """test that a token is not created when invalid credentials"""

        payload = self.generic_payload

        create_user(**self.generic_payload)

        payload['email'] = 'changed@email.com'

        response = self.client.post(TOKEN_URL, self.generic_payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """test that token is not created when no user is created"""

        response = self.client.post(TOKEN_URL, self.generic_payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """test that email and password are required"""
        payload = self.generic_payload
        payload['password'] = ''

        response = self.client.post(TOKEN_URL, self.generic_payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """tests that authentication is required"""

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUsersApiTests(TestCase):
    """Test api requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email = 'test@test.com',
            password = 'myPassword',
            name = 'my name'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        """test that retriving the user profile works"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """test that post is disabled ME_URL"""

        response = self.client.post(ME_URL, {})
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user(self):
        """test that the user profile is updated correctly"""
        payload = {
            'name': 'new name',
            'password': 'new password',
        }

        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
