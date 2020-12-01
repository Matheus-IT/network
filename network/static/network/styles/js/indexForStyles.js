document.addEventListener('DOMContentLoaded', function() {
	const newPost = document.querySelector('#newPost');
	const postButton = document.querySelector('#submitNewPost');

	if (newPost) {
		const borderRadiusBefore = newPost.style.borderRadius;
	
		newPost.addEventListener('focus', function() {
			postButton.style.alignSelf = 'flex-end';
			newPost.style.borderRadius = '0.4em';
		});
	
		newPost.addEventListener('focusout', function() {
			postButton.style.alignSelf = 'center';
			newPost.style.borderRadius = borderRadiusBefore;
		});
	}
});
