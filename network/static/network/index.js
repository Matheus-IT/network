document.addEventListener('DOMContentLoaded', function() {
	const submitNewPost = document.querySelector('#submitNewPost');
	submitNewPost.addEventListener('click', (e) => handleSubmitNewPost(e));
});

function handleSubmitNewPost(event) {
	event.preventDefault();
	console.log('New Post!');
}
