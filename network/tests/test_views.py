from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from ..models import User, Follower


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

		self.mock_user1 = {
			'username': 'test_user1',
			'password': '12345',
			'email': 'test_user1@example.com'
		}
		self.mock_user2 = {
			'username': 'test_user2',
			'password': '12345',
			'email': 'test_user2@example.com'
		}
	
	def createUser(self, user):
		return User.objects.create_user(
			username=user['username'],
			password=user['password'],
			email=user['email']
		)

	def test_get(self):
		from ..views import ProfilePage

		# user_follower and user_being_followed receive instances of User
		Follower.objects.create(
			user_follower=self.createUser(self.mock_user1),
			user_being_followed=self.createUser(self.mock_user2)
		)
		visitor_is_following_this_profile = True

		# mock_user1 is visiting mock_user2
		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		response = self.client.get(reverse('profilePage', kwargs={'profileId': 2}))

		self.assertEqual(visitor_is_following_this_profile, response.context['visitor_is_following'])
		self.assertEqual(response.status_code, 200)

	def test_fail_get(self):
		""" This case should fail because this profile id doesn't exist in the database """
		response = self.client.get(reverse('profilePage', kwargs={'profileId': 0}))

		self.assertEqual(response.status_code, 404)


class Login(TestCase):
	def setUp(self):
		self.mock_user = User.objects.create_user(
			username='test_user', password='12345', email='test_user@example.com'
		)
	
	def hasWarning(self, response):
		""" for registered users, the login should be successful, without warning message.
			if there is a warning message something wrong happaned """
		try:
			warning_message = response.context['message']
			# no warning message == TypeError
		except TypeError:
			warning_message = False
		return warning_message
	
	def test_get(self):
		response = self.client.get(reverse('login'))

		self.assertEqual(response.status_code, 200)
	
	def test_post(self):
		data = {
			'username': 'test_user',
			'password': '12345'
		}

		response = self.client.post(reverse('login'), data)

		warning_message = self.hasWarning(response)
		self.assertFalse(warning_message)
	
	def test_fail_post(self):
		""" If the user try to login without being registered, this user should
			receive a warning message """
		
		data = {
			'username': 'fail_user',
			'password': '000000'
		}

		response = self.client.post(reverse('login'),  data)

		warning_message = self.hasWarning(response)
		self.assertTrue(warning_message)
	

class Logout(TestCase):
	def test_get(self):
		response = self.client.get(reverse('logout'), follow=True)
		self.assertEqual(response.status_code, 200)


class Register(TestCase):
	def setUp(self):
		self.mock_user = User.objects.create_user(
			username='test_user', password='12345', email='test_user@example.com'
		)
	
	def hasWarning(self, response):
		""" for new users, the registration should be successful, without warning message.
			if there is a warning message something went wrong """
		try:
			warning_message = response.context['message']
			# no warning message == TypeError
		except TypeError:
			warning_message = False
		return warning_message
	
	def test_get(self):
		response = self.client.get(reverse('register'))
	
		self.assertEqual(response.status_code, 200)
	
	def test_post(self):
		data = {
			'username': 'new_test_user',
			'email': 'test@example.com',
			'password': '12345',
			'confirmation': '12345'
		}

		response = self.client.post(reverse('register'), data, follow=True)
		self.assertEqual(response.status_code, 200)

	def test_fail_post(self):
		""" This case should fail because this user already exists in the database """
		
		data = {
			'username': self.mock_user.username,
			'email': self.mock_user.email,
			'password': self.mock_user.password,
			'confirmation': self.mock_user.password
		}

		response = self.client.post(reverse('register'), data, follow=True)

		warning_message = self.hasWarning(response)

		self.assertTrue(warning_message)