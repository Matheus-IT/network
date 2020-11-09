from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from ..models import User


class Index(TestCase):
	def setUp(self):
		self.client = Client()
		self.factory = RequestFactory()
		self.mock_user = User.objects.create_user(
			username='test_user', password='12345', email='test_user@example.com'
		)
	
	def test_get(self):
		response = self.client.get(reverse('index'))
		
		self.assertEqual(response.status_code, 200)
	
	def test_post(self):
		from ..views import index

		request = self.factory.post(reverse('index'))

		request.user = self.mock_user
		request.data = {'newPostContent': 'New post for testing'}

		response = index(request)

		self.assertEqual(response.status_code, 200)
	
	def test_fail_post(self):
		""" this response should fail because this user is not registered in the database """
		from ..views import index

		request = self.factory.post(reverse('index'))

		request.user = AnonymousUser()
		request.data = {'newPostContent': 'blabalbalababal'}

		response = index(request)

		self.assertEqual(response.status_code, 403)


class ProfilePage(TestCase):
	def setUp(self):
		self.client = Client()
		self.mock_user = User.objects.create_user(
			username='test_user', password='12345', email='test_user@example.com'
		)
	
	def test_get(self):
		response = self.client.get(reverse('profilePage', kwargs={'profileId': 1}))

		self.assertEqual(response.status_code, 200)
	
	def test_fail_get(self):
		""" This test should fail because this profile id doesn't exist in the database """
		response = self.client.get(reverse('profilePage', kwargs={'profileId': 0}))

		self.assertEqual(response.status_code, 404)
	