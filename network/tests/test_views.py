from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

import json

from ..models import User, Follower, Post


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

	def test_bad_post(self):
		""" this response should fail because this user is not registered in the database """
		from ..views import index

		request = self.factory.post(reverse('index'))

		request.user = AnonymousUser()
		request.data = {'newPostContent': 'blabalbalababal'}

		response = index(request)

		self.assertEqual(response.status_code, 403)


class GetPostsPage(TestCase):
	def setUp(self):
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
		self.mock_user3 = {
			'username': 'test_user3',
			'password': '12345',
			'email': 'test_user3@example.com'
		}

		self.mock_User1 = self.createUser(self.mock_user1)
		self.mock_User2 = self.createUser(self.mock_user2)
		self.mock_User3 = self.createUser(self.mock_user3)

		# the user1 makes some posts for test proposes
		self.generatePosts(15, self.mock_User1)
		self.generatePosts(15, self.mock_User2)
	
	def createUser(self, user):
		return User.objects.create_user(
			username=user['username'],
			password=user['password'],
			email=user['email']
		)
	
	def generatePosts(self, numPosts, user):
		for i in range(numPosts):
			newPostContent = f'content {i}'

			newPost = Post.objects.create(
				poster=user,
				content=newPostContent
			)
			newPost.save()
	
	def are_all_these_posts_from_this_user(self, posts, user):
		for post in posts:
			if post['poster']['id'] != user.id:
				return False
		return True

	def areAllThesePostsFromProfilesTheCurrentUserFollows(self, posts, user):
		follow_objects = user.users_being_followed.all()
		# get a list of users ids that the given user follows
		users_followed_ids = [follow.user_being_followed.id for follow in follow_objects]

		for post in posts:
			if post['poster']['id'] in users_followed_ids:
				continue
			else:
				return False
		return True

	def test_get_posts_from_index_first_page(self):
		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		response = self.client.get(reverse('getPostsPageGivenTemplate', kwargs={
			'templatePageName': 'index',
			'pageNumber': 1
		}))

		self.assertEqual(response.status_code, 200)
	
	def test_bad_get_posts_from_index_of_a_non_existing_page_number(self):
		""" This case should fail because I'm trying to get a 
			page of posts that doesn't exist """
		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		response = self.client.get(reverse('getPostsPageGivenTemplate', kwargs={
			'templatePageName': 'index',
			'pageNumber': 5 # this page doesn't exist
		}))

		self.assertEqual(response.status_code, 404)
	
	def test_get_posts_for_first_page_of_page_following(self):
		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		follow = Follower.objects.create(
			user_follower = self.mock_User1,
			user_being_followed = self.mock_User2 
		)

		response = self.client.get(reverse('getPostsPageGivenTemplate', kwargs={
			'templatePageName': 'following',
			'pageNumber': 1
		}))

		# get a list of users being followed by the current user
		follow_objects = self.mock_User1.users_being_followed.all()
		followed_by_current_user = [follow.user_being_followed for follow in follow_objects]
		
		# get a list of posts made by the users that the current user follows
		serialized_posts = [post.serialize() for post in Post.objects.order_by('-timestamp').all()[:10] if post.poster in followed_by_current_user]

		result = self.areAllThesePostsFromProfilesTheCurrentUserFollows(serialized_posts, self.mock_User1)

		self.assertTrue(result)
		self.assertEqual(response.status_code, 200)
	
	def test_get_first_posts_page_from_a_profile(self):
		# mock_user2 requests some posts from mock_user1
		self.client.login(
			username=self.mock_user2['username'],
			password=self.mock_user2['password']
		)

		response = self.client.get(reverse('getPostsPageGivenUserId', kwargs={
			'pageNumber': 1,
			'filterUserId': self.mock_User1.id
		}))

		parsed_response = response.json()
		posts = [post for post in parsed_response['currentPagePosts']]

		result = self.are_all_these_posts_from_this_user(posts, self.mock_User1)
		
		self.assertTrue(result)
		self.assertEqual(response.status_code, 200)
	
	def test_bad_get_posts_given_a_page_number_and_a_non_existing_profile_id(self):
		""" this case fails because mock_user1 requests some posts
			from a non existing user """
		self.client.login(
			username=self.mock_user2['username'],
			password=self.mock_user2['password']
		)

		response = self.client.get(reverse('getPostsPageGivenUserId', kwargs={
			'pageNumber': 1,
			'filterUserId': 5 # this user id doesn't exist
		}))
		
		self.assertEqual(response.status_code, 404)


class HandleLikeDislike(TestCase):
	def setUp(self):
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

		self.mock_User1 = self.createUser(self.mock_user1)
		self.mock_User2 = self.createUser(self.mock_user2)

		# the user makes some posts for test proposes
		self.generatePosts(3, self.mock_User2)

	def createUser(self, user):
		return User.objects.create_user(
			username=user['username'],
			password=user['password'],
			email=user['email']
		)
	
	def generatePosts(self, numPosts, user):
		for i in range(numPosts):
			newPostContent = f'content {i}'

			newPost = Post.objects.create(
				poster=user,
				content=newPostContent
			)
			newPost.save()
	
	def doesThisUserLikeThisPost(self, user, post):
		for like in post['likes']:
			if user.id == like['liker_id']:
				return True
		return False

	def test_like_a_particular_post(self):
		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		post = Post.objects.get(id=1)
		post = post.serialize()

		does_current_visitor_like_this_post = self.doesThisUserLikeThisPost(self.mock_User1, post)

		data = json.dumps({
			'does_current_visitor_like_this_post': not does_current_visitor_like_this_post,
			'number_likes': post['number_likes']
		})

		response = self.client.put(reverse('handleLikeDislike', kwargs={'postId': self.mock_User1.id}), data)

		self.assertEqual(response.status_code, 200)
	
	def test_bad_like_a_particular_post_when_already_liking(self):
		""" This test case should raise an exception because the visitor already likes this post
			and is trying to like it again """
		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		post = Post.objects.get(id=1).serialize()

		# At first, the visitor doesn't like this post, then he likes the post
		does_current_visitor_like_this_post = self.doesThisUserLikeThisPost(self.mock_User1, post)
		

		data = json.dumps({
			'does_current_visitor_like_this_post': not does_current_visitor_like_this_post,
			'number_likes': post['number_likes']
		})
		# request to like this post
		response = self.client.put(reverse('handleLikeDislike', kwargs={'postId': self.mock_User1.id}), data)

		# And then the visitor tries to like again, so he's gonna receive an exception
		response_post = response.json()

		does_current_visitor_like_this_post = self.doesThisUserLikeThisPost(self.mock_User1, response_post)


		data = json.dumps({
			'does_current_visitor_like_this_post': does_current_visitor_like_this_post,
			'number_likes': response_post['number_likes']
		})
		# request to like this post again
		response = self.client.put(reverse('handleLikeDislike', kwargs={'postId': self.mock_User1.id}), data)

		self.assertEqual(response.status_code, 400)
	
	def test_dislike_a_particular_post(self):
		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		post = Post.objects.get(id=1).serialize()

		# At first, the visitor doesn't like this post, then he likes the post
		does_current_visitor_like_this_post = self.doesThisUserLikeThisPost(self.mock_User1, post)

		data = json.dumps({
			'does_current_visitor_like_this_post': not does_current_visitor_like_this_post,
			'number_likes': post['number_likes']
		})
		# request to like this post
		response = self.client.put(reverse('handleLikeDislike', kwargs={'postId': self.mock_User1.id}), data)

		# And then the visitor tries to dislike the post
		response_post = response.json()
		
		does_current_visitor_like_this_post = self.doesThisUserLikeThisPost(self.mock_User1, response_post)

		data = json.dumps({
			'does_current_visitor_like_this_post': not does_current_visitor_like_this_post,
			'number_likes': response_post['number_likes']
		})
		# request to dislike this post again
		response = self.client.put(reverse('handleLikeDislike', kwargs={'postId': self.mock_User1.id}), data)

		self.assertEqual(response.status_code, 200)
	
	def test_bad_dislike_a_particular_post_when_the_visitor_already_dislike_it(self):
		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		post = Post.objects.get(id=1).serialize()

		# At first, the visitor doesn't like this post, then he tries to dislike it
		does_current_visitor_like_this_post = self.doesThisUserLikeThisPost(self.mock_User1, post)

		data = json.dumps({
			'does_current_visitor_like_this_post': does_current_visitor_like_this_post,
			'number_likes': post['number_likes']
		})
		# request to dislike this post
		response = self.client.put(reverse('handleLikeDislike', kwargs={'postId': self.mock_User1.id}), data)

		self.assertEqual(response.status_code, 400)


class HandleSaveNewPostContent(TestCase):
	def setUp(self):
		self.mock_user = {
			'username': 'test_user',
			'password': '12345',
			'email': 'test_user@example.com'
		}

		self.mock_User = self.createUser(self.mock_user)

		self.test_post = Post.objects.create(poster=self.mock_User, content='test post content')

	def createUser(self, user):
		return User.objects.create_user(
			username=user['username'],
			password=user['password'],
			email=user['email']
		)
	
	def test_save_new_post_content(self):
		self.client.login(
			username = self.mock_user['username'],
			password = self.mock_user['password']
		)

		data = json.dumps({'newContent': 'new content for tests'})
		response = self.client.put(reverse('handleSaveNewPostContent', kwargs={'postId': self.test_post.id}), data)
		self.assertEqual(response.status_code, 200)
	
	def test_bad_save_new_post_content_when_wrong_post_id(self):
		""" This case should fail because the post id doesn't exist """
		self.client.login(
			username = self.mock_user['username'],
			password = self.mock_user['password']
		)

		data = json.dumps({'newContent': 'new content for tests'})
		response = self.client.put(reverse('handleSaveNewPostContent', kwargs={'postId': 5}), data)
		self.assertEqual(response.status_code, 404)
	
	def test_bad_save_new_post_content_when_blank_new_content(self):
		""" This case should fail because it's trying to send a new content blank """
		self.client.login(
			username = self.mock_user['username'],
			password = self.mock_user['password']
		)

		data = json.dumps({'newContent': ''})
		response = self.client.put(reverse('handleSaveNewPostContent', kwargs={'postId': self.test_post.id}), data)
		self.assertEqual(response.status_code, 400)
	
	def test_bad_save_new_post_content_when_unauthorized_user(self):
		""" This case should fail because the user is not authenticated """

		data = json.dumps({'newContent': 'new content for tests'})
		response = self.client.put(reverse('handleSaveNewPostContent', kwargs={'postId': self.test_post.id}), data)
		self.assertEqual(response.status_code, 302)


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

	def test_bad_get(self):
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

		self.assertEqual(response.status_code, 200)

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

		self.assertEqual(response.status_code, 200)

	def test_bad_put_when_request_for_visitor_to_unfollow_the_current_profile(self):
		""" The visitor IS NOT following the current profile, then he makes a PUT request
		 	for profilePage to make it UNFOLLOW this profile """
		mock_User1 = self.createUser(self.mock_user1)
		mock_User2 = self.createUser(self.mock_user2)

		self.client.login(
			username=self.mock_user1['username'],
			password=self.mock_user1['password']
		)

		visitor_is_following = False

		data = json.dumps({
			'visitor_is_following': visitor_is_following
		})
		response = self.client.put(reverse('profilePage', kwargs={'profileId': mock_User2.id}), data)

		self.assertEqual(response.status_code, 400)

	def test_bad_put_when_request_for_visitor_to_follow_the_current_profile(self):
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

	def test_bad_put(self):
		""" This case should fail because it tries to put to a profile id that doesn't exist """
		response = self.client.put('profilePage', kwargs={'profileId': 0})

		self.assertEqual(response.status_code, 404)


class FollowingPage(TestCase):
	def setUp(self):
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
		self.createUser(self.mock_user1)
		self.client.login(
			username = self.mock_user1['username'],
			password = self.mock_user1['password']
		)
		response = self.client.get(reverse('followingPage'))
		
		self.assertEqual(response.status_code, 200)

	def test_bad_get(self):
		response = self.client.get(reverse('followingPage'))
		self.assertEqual(response.status_code, 302)


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

	def test_post_login(self):
		data = {
			'username': 'test_user',
			'password': '12345'
		}

		response = self.client.post(reverse('login'), data)

		warning_message = self.hasWarning(response)
		self.assertFalse(warning_message)

	def test_bad_post_login(self):
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

	def test_post_register(self):
		data = {
			'username': 'new_test_user',
			'email': 'test@example.com',
			'password': '12345',
			'confirmation': '12345'
		}

		response = self.client.post(reverse('register'), data, follow=True)
		self.assertEqual(response.status_code, 200)

	def test_bad_post_register(self):
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
