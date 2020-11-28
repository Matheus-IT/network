/* JAVASCRIPT RELATED TO POSTS STUFF */
function fetchPostsPage(pageNumber) {
	let fetchPromise;

	try {
		// fetch posts for profile page, global variable 'profileId' from django
		fetchPromise = fetch(`/getPostsProfilePage/${profileId}/${pageNumber}`);
	} catch(err) {
		if (err.name === 'ReferenceError') {
			// If the 'profileId' wasn't defined it means we're on another page, given a template page name
			fetchPromise = fetch(`/getPostsPage/${templatePageName}/${pageNumber}`);
		} else {
			console.log(err);
		}
	}

	fetchPromise
	.then(response => response.json())
	.then(postsPage => {
		generatePosts(postsPage.currentPagePosts);

		handleHideShowNavigationButton(postsPage.hasPrevious, 'previousPage');
		handleHideShowNavigationButton(postsPage.hasNext, 'nextPage');
	})
	.catch(err => console.log(err));
}

function generatePosts(currentPagePostsData) {
	const postsContainer = document.querySelector('#postsWrapper');
	
	postsContainer.innerHTML = '';
	currentPagePostsData.forEach(postData => {
		const post = document.createElement('div');
		
		post.setAttribute('class', 'post');
		post.setAttribute('id', `post${postData.id}`);
		post.innerHTML = `
			<h3>
				<a href="/profile/${postData.poster.id}">${postData.poster.username}</a> says
			</h3>
			<p>${postData.content}</p>
			<em>${postData.timestamp}</em>
			<br>
		`;
		
		if (isUserAuthenticated) {
			const likeIcon = generateLikeIcon(postData);
			post.append(likeIcon);

			// add the event handler when the like icon is available
			observeElementResolveWhenAvailable(`#likeIcon${postData.id}`)
			.then(likeIcon => likeIcon.onclick = () => handleLikeDislike(postData))
			.catch(err => console.log(err));
		}

		post.innerHTML += `
			<strong class="numLikes">${postData.number_likes}</strong>
		`;

		if (isUserAuthenticated) {
			const editIcon = document.createElement('img');

			editIcon.setAttribute('class', 'editIcon');
			editIcon.setAttribute('id', `editIcon${postData.id}`);
			editIcon.setAttribute('src', editIconSource);
			post.append(editIcon);
		}

		postsContainer.append(post);
	});
}

function handleHideShowNavigationButton(hasThisPage, navigationButtonId) {
	const navigationButton = document.querySelector(`#${navigationButtonId}`);
	
	if (hasThisPage)
		navigationButton.style.display = 'block';
	else
		navigationButton.style.display = 'none'
}

function generateLikeIcon(postData) {
	let likeIcon = document.createElement('img');

	likeIcon.setAttribute('class', 'likeIcon');
	likeIcon.setAttribute('id', `likeIcon${postData.id}`);
	
	if (postData.does_current_visitor_like_this_post) {
		// global icon variables
		likeIcon.setAttribute('src', solidHeartIconSource);
	} else {
		likeIcon.setAttribute('src', openHeartIconSource);
	}
	
	return likeIcon;
}

function observeElementResolveWhenAvailable(selector) {
	return new Promise((resolve, reject) => {
		const observer = new MutationObserver(function(mutationsList, observer) {
			const element = document.querySelector(selector);
			
			// verify if the element is available
			if (element) {
				observer.disconnect();
				resolve(element);
			}
		});

		// the observer is going to watch for document changes
		const targetNode = document;
		const config = { childList: true, subtree: true };

		observer.observe(targetNode, config); 
	});
}

function handleLikeDislike(postData) {            
	if (postData.does_current_visitor_like_this_post) {
		// dislike
		postData.number_likes--;
	} else {
		// like
		postData.number_likes++;
	}
	
	postData.does_current_visitor_like_this_post = ! postData.does_current_visitor_like_this_post;

	fetch(`/handleLikeDislike/${postData.id}`, {
		method: 'PUT',
		body: JSON.stringify({
			does_current_visitor_like_this_post: postData.does_current_visitor_like_this_post,
			number_likes: postData.number_likes
		}),
		headers: {
			// getCookie from utility functions
			'X-CSRFToken': getCookie('csrftoken')
		}
	})
	.then(response => response.json())
	.then(data => {
		const post = document.querySelector(`#post${data.id}`);

		post.querySelector('.numLikes').innerHTML = data.number_likes;

		const likeIcon = post.querySelector(`#likeIcon${data.id}`);

		if (postData.does_current_visitor_like_this_post) {
			// global icon variables
			likeIcon.setAttribute('src', solidHeartIconSource);
		} else {
			likeIcon.setAttribute('src', openHeartIconSource);
		}
	})
	.catch(err => console.log(err));
}
