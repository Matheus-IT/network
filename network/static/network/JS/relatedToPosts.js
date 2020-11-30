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
			<div class="contentContainer">
				<p>${postData.content}</p>
			</div>
			<em class="timestamp">${postData.timestamp}</em>
			<br>
			<div class="icons">
				<div class="likeContainer">
				</div>

				<div class="actionsContainer">
				</div>
			</div>
		`;
		
		if (isUserAuthenticated) {
			const likeIcon = generateIcon('likeIcon', postData.id);
			
			if (postData.does_current_visitor_like_this_post) {
				// global icon source variables
				likeIcon.setAttribute('src', solidHeartIconSource);
			} else {
				likeIcon.setAttribute('src', openHeartIconSource);
			}
			post.querySelector('.likeContainer').append(likeIcon);

			// add the event handler when the like icon is available
			observeElementResolveWhenAvailable(`#likeIcon${postData.id}`)
			.then(likeIcon => likeIcon.onclick = () => handleLikeDislike(postData))
			.catch(err => console.log(err));
		}

		post.querySelector('.likeContainer').innerHTML += `
			<strong class="numLikes">${postData.number_likes}</strong>
		`;

		if (isUserAuthenticated && isUserThePoster(postData.poster)) {
			const editIcon = generateIcon('editIcon', postData.id);

			// global icon source variable
			editIcon.setAttribute('src', editIconSource);
			editIcon.addEventListener('click', () => handleEditPost(post, postData));
			post.querySelector('.actionsContainer').append(editIcon);
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

function generateIcon(name, identifier) {
	/* returns an icon given a name and a identifier */
	let icon = document.createElement('img');

	icon.setAttribute('class', `${name}`);
	icon.setAttribute('id', `${name}${identifier}`);
	return icon;
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

function handleEditPost(post, postData) {
	const postContentContainer = post.querySelector(`.contentContainer`);
	const postContent = postContentContainer.querySelector('p').innerHTML;
	const editIcon = post.querySelector(`#editIcon${postData.id}`);
	editIcon.style.display = 'none';
	
	const editArea = document.createElement('textarea');
	editArea.setAttribute('id', `editArea${postData.id}`);
	editArea.setAttribute('rows', '5');
	editArea.setAttribute('columns', '15');
	editArea.innerHTML = postContent;
	
	postContentContainer.innerHTML = '';
	postContentContainer.append(editArea);
	
	const actionsContainer = post.querySelector('.actionsContainer');

	const saveIcon = generateIcon('saveIcon', postData.id);
	// global icon source variable
	saveIcon.setAttribute('src', saveIconSource);
	saveIcon.addEventListener('click', () => handleSaveNewPostContent(post, postData));
	actionsContainer.append(saveIcon);

	const cancelIcon = generateIcon('cancelIcon', postData.id);
	cancelIcon.setAttribute('src', cancelIconSource);
	cancelIcon.addEventListener('click', () => handleCancelEditPost(postContent, post, editIcon));
	actionsContainer.append(cancelIcon);

	console.log(postContent + ' editing...');
}

function handleSaveNewPostContent(post, postData) {
	const newContent = post.querySelector(`#editArea${postData.id}`).value;

	fetch(`/handleSaveNewPostContent/${postData.id}`, {
		method: 'PUT',
		body: JSON.stringify({
			newContent: newContent
		}),
		headers: {
			// getCookie from utility functions
			'X-CSRFToken': getCookie('csrftoken')
		}
	})
	.then(response => response.json())
	.then(data => {
		console.log(data);

		post.querySelector('.contentContainer').innerHTML = `<p>${newContent}</p>`;

		post.querySelector('.timestamp').innerHTML = data.timestamp;

		const editIcon = post.querySelector(`#editIcon${postData.id}`);
		editIcon.style.display = 'block';
		post.querySelector('.actionsContainer').innerHTML = '';
		post.querySelector('.actionsContainer').append(editIcon);
	})
	.catch(err => console.log(err));
}

function handleCancelEditPost(postContent, post, editIcon) {
	post.querySelector('.contentContainer').innerHTML = `<p>${postContent}</p>`;

	editIcon.style.display = 'block';
	post.querySelector('.actionsContainer').innerHTML = '';
	post.querySelector('.actionsContainer').append(editIcon);
}

function isUserThePoster(poster) {
	return poster.username === userUsername;
}
