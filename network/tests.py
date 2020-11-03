from django.test import Client, TestCase
from django.urls import reverse

from .models import User

# Create your tests here.
class ViewsTestCase(TestCase):
	client = Client()

	def setUp(self):
		mock_user = User.objects.create_user(username='test_user', password='12345')

	def test_get_index(self):
		response = self.client.get(reverse('index'))
		self.assertEqual(response.status_code, 200)
	
	def test_get_login_view(self):
		response = self.client.get(reverse('login'))
		self.assertEqual(response.status_code, 200)
	
	def test_post_login_view(self):
		data = {
			'username': 'test_user',
			'password': '12345'
		}

		response = self.client.post(reverse('login'), data)

		# for registered users, the login should be successful, without warning message
		try:
			warning_message = response.context['message']
			# no warning message == TypeError
		except TypeError:
			warning_message = False

		self.assertFalse(warning_message)
	
	def test_fail_post_login_view(self):
		data = {
			'username': 'fail_user',
			'password': '000000'
		}

		response = self.client.post(reverse('login'),  data)

		try:
			warning_message = response.context['message']
		except TypeError:
			warning_message = False
		
		self.assertTrue(warning_message)
	
	def test_logout_view(self):
		response = self.client.get(reverse('logout'))

		# I don't know why is 302, but...
		self.assertEqual(response.status_code, 302)
	
	def test_get_register_view(self):
		response = self.client.get(reverse('register'))
		self.assertEqual(response.status_code, 200)
