/* JAVASCRIPT RELATED TO FOLLOW */
document.addEventListener('DOMContentLoaded', function() {
	const followBtn = document.querySelector('#followBtn');
	
	if (followBtn !== null)
		followBtn.onclick = toggleFollowUnfollow;
});

function toggleFollowUnfollow() {
	// using global 'profileId' from django
	fetch(`/profile/${profileId}`, {
		method: 'PUT',
		body: JSON.stringify({
			// using global 'visitorIsFollowing' from django
			visitor_is_following: ! visitorIsFollowing,
		}),
		headers: {
			// utility function getCookie
			'X-CSRFToken': getCookie('csrftoken')
		}
	})
	.then(response => response.json())
	.then(data => {
		// global variable 'visitorIsFollowing'
		visitorIsFollowing = ! visitorIsFollowing;
		// update information because visitorIsFollowing has changed
		updateNumOfFollowers(visitorIsFollowing);
		updateFollowButton(visitorIsFollowing);
	})
	.catch(err => console.log(err));
}

function updateNumOfFollowers(visitorIsFollowing) {
	// using global 'numOfFollowers' from django
	if (visitorIsFollowing)
		numOfFollowers++;
	else
		numOfFollowers--;
	
	document.querySelector('#followers').innerHTML = numOfFollowers;
}

function updateFollowButton(visitorIsFollowing) {
	const followBtn = document.querySelector('#followBtn');

	if (visitorIsFollowing)
		followBtn.innerHTML = 'Unfollow';
	else
		followBtn.innerHTML = 'Follow';
}