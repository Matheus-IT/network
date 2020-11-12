from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

import json

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

	def test_get_when_visitor_is_following(self):
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

	def test_get_when_visitor_is_not_following(self):
		self.createUser(self.mock_user1)
		self.createUser(self.mock_user2)

		# mock_user2 is visiting mock_user1, but mock_user2 is not following mock_user1
		visitor_is_following_this_profile = False
		result = self.client.login(
			username=self.mock_user2['username'],
			password=self.mock_user2['password']
		)

		response = self.client.get(reverse('profilePage', kwargs={'profileId': 1}))

		self.assertEqual(visitor_is_following_this_profile, response.context['visitor_is_following'])
		self.assertEqual(response.status_code, 200)

	def test_fail_get(self):
		""" This case should fail because this profile id doesn't exist in the database """
		response = self.client.get(reverse('profilePage', kwargs={'profileId': 0}))

		self.assertEqual(response.status_code, 404)

	def test_put_when_request_for_visitor_to_follow_the_current_profile(self):
		""" The visitor is not following the current profile, then he makes a PUT request
		 	for profilePage to make it follow this profile """
		mock_User1 = self.createUser(self.mock_user1)
		mock_User2 = self.createUser(self.mock_user2)

		self.client.login(
			username=self.mock_user2['username'],
			password=self.mock_user2['password']
		)
		visitor_is_following = False

		data = json.dumps({
			# I used 'not' to toggle between True and False
			"visitor_is_following": not visitor_is_following
		})
		response = self.client.put(reverse('profilePage', kwargs={'profileId': mock_User1.id}), data)

		self.assertEqual(response.status_code, 204)

	def test_put_when_request_for_visitor_to_unfollow_the_current_profile(self):
		""" The visitor IS following the current profile, then he makes a PUT request
		 	for profilePage to make it UNFOLLOW this profile """
		mock_User1 = self.createUser(self.mock_user1)
		mock_User2 = self.createUser(self.mock_user2)

		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		Follower.objects.create(
			user_follower = mock_User1,
			user_being_followed = mock_User2
		)
		visitor_is_following = True

		data = json.dumps({
			# I used 'not' to toggle between True and False
			'visitor_is_following': not visitor_is_following
		})
		response = self.client.put(reverse('profilePage', kwargs={'profileId': mock_User2.id}), data)

		self.assertEqual(response.status_code, 204)

	def test_fail_put_when_request_for_visitor_to_follow_the_current_profile(self):
		""" This test case should fail because the visitor IS following the current profile, then he
			makes a PUT request	for profilePage to make it FOLLOW this profile """
		mock_User1 = self.createUser(self.mock_user1)
		mock_User2 = self.createUser(self.mock_user2)

		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		Follower.objects.create(
			user_follower = mock_User1,
			user_being_followed = mock_User2
		)
		visitor_is_following = True

		data = json.dumps({
			'visitor_is_following': visitor_is_following
		})
		response = self.client.put(reverse('profilePage', kwargs={'profileId': mock_User2.id}), data)

		self.assertEqual(response.status_code, 400)

	def test_fail_put(self):
		""" This case should fail because it tries to put to a profile id that doesn't exist """
		response = self.client.put('profilePage', kwargs={'profileId': 0})

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
