import email
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'super@email.com',
            password = 'pass'
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'user@email.com',
            password = 'pass',
            name = 'full name'
        )

    def test_user_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])

        result = self.client.get(url)

        self.assertEqual(result.status_code, 200)

    def test_create_user_page(self):
        """tests that the create user page works"""
        url = reverse('admin:core_user_add')

        result = self.client.get(url)

        self.assertEqual(result.status_code, 200)
