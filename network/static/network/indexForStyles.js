document.addEventListener('DOMContentLoaded', function() {
	const newPost = document.querySelector('#newPost');
	const newPostLabel = document.querySelector('#newPostLabel');
	const postButton = document.querySelector('#submitNewPost');
	
	newPost.addEventListener('focus', function() {
		newPostLabel.style.display = 'none';
		postButton.style.alignSelf = 'flex-end';
	});

	newPost.addEventListener('focusout', function() {
		newPostLabel.style.display = 'block';
		postButton.style.alignSelf = 'center';
	});
});
