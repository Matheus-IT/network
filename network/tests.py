from django.test import Client, TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from .models import User

# Create your tests here.
class ViewsTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.factory = RequestFactory()
		self.mock_user = User.objects.create_user(
			username='test_user', password='12345', email='test_user@example.com'
		)

	def hasWarning(self, response):
		# for registered users, the login should be successful, without warning message
		try:
			warning_message = response.context['message']
			# no warning message == TypeError
		except TypeError:
			warning_message = False
		return warning_message

	# TESTS FOR INDEX VIEW
	def test_get_index(self):
		response = self.client.get(reverse('index'))
		self.assertEqual(response.status_code, 200)

	def test_post_index(self):
		from .views import index

		request = self.factory.post(reverse('index'))

		request.user = self.mock_user
		request.data = {'newPostContent': 'New post for testing'}

		response = index(request)

		self.assertEqual(response.status_code, 200)

	def test_fail_post_index(self):
		from .views import index

		request = self.factory.post(reverse('index'))

		# this should fail because this user is not registered in the database
		request.user = AnonymousUser()
		request.data = {'newPostContent': 'blabalbalababal'}

		response = index(request)

		self.assertEqual(response.status_code, 403)

	# TESTS FOR LOGIN VIEW
	def test_get_login_view(self):
		response = self.client.get(reverse('login'))
		self.assertEqual(response.status_code, 200)

	def test_post_login_view(self):
		data = {
			'username': 'test_user',
			'password': '12345'
		}

		response = self.client.post(reverse('login'), data)

		warning_message = self.hasWarning(response)
		self.assertFalse(warning_message)

	def test_fail_post_login_view(self):
		data = {
			'username': 'fail_user',
			'password': '000000'
		}

		response = self.client.post(reverse('login'),  data)

		warning_message = self.hasWarning(response)
		self.assertTrue(warning_message)

	# TESTS FOR LOGOUT VIEW
	def test_logout_view(self):
		response = self.client.get(reverse('logout'), follow=True)
		self.assertEqual(response.status_code, 200)

	# TESTS FOR REGISTER VIEW
	def test_get_register_view(self):
		response = self.client.get(reverse('register'))
		self.assertEqual(response.status_code, 200)

	def test_post_register_view(self):
		data = {
			'username': 'new_test_user',
			'email': 'test@example.com',
			'password': '12345',
			'confirmation': '12345'
		}

		response = self.client.post(reverse('register'), data, follow=True)
		self.assertEqual(response.status_code, 200)

	def test_fail_post_register_view(self):
		data = {
			'username': 'test_user',
			'email': 'test_user@example.com',
			'password': '12345',
			'confirmation': '12345'
		}

		response = self.client.post(reverse('register'), data, follow=True)

		warning_message = self.hasWarning(response)

		self.assertTrue(warning_message)
