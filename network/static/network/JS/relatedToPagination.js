/* JAVASCRIPT RELATED TO PAGINATION */
document.addEventListener('DOMContentLoaded', function() {
	// navigate to the first page when first time
	navigateTo(1);
	markAsActiveForPagination(currentNavigationPage);
	
	document.querySelectorAll('.page-number').forEach((pageNum) => {
		pageNum.addEventListener('click', handlePaginationByNumbers);
	});

	document.querySelector('#previousPage').addEventListener('click', handlePaginateToPreviousPage);
	document.querySelector('#nextPage').addEventListener('click', handlePaginateToNextPage);
});

function handlePaginationByNumbers() {
	const pageNumber = this.innerHTML;
	navigateTo(pageNumber);

	deactivateAllFromPagination('.page-item');
	markAsActiveForPagination(currentNavigationPage);
}

function handlePaginateToPreviousPage() {
	currentNavigationPage--;
	navigateTo(currentNavigationPage);

	deactivateAllFromPagination('.page-item');
	markAsActiveForPagination(currentNavigationPage);
}

function handlePaginateToNextPage() {
	currentNavigationPage++;
	navigateTo(currentNavigationPage);

	deactivateAllFromPagination('.page-item');
	markAsActiveForPagination(currentNavigationPage);
}

function navigateTo(pageNumber) {
	// fetchPostsPage is from 'relatedToPosts.js'
	fetchPostsPage(pageNumber);
	currentNavigationPage = pageNumber;
	goToTheTop();
}

async function goToTheTop() {
	// document.body.scrollTop // For Safari
	// document.documentElement.scrollTop // For Chrome, Firefox, IE and Opera
	while (document.body.scrollTop != 0 || document.documentElement.scrollTop != 0) {
		await sleep(1);
		window.scrollBy(0, -100);
	}
}

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

function deactivateAllFromPagination(className) {
	const pageItems = document.querySelectorAll(className);
	
	pageItems.forEach(item => {
		item.classList.remove('active');
	});
}

function markAsActiveForPagination(currentPageNumber) {
	navigationNumberButtons = document.querySelectorAll('.page-number');

	navigationNumberButtons.forEach(pageNumButton => {
		if (pageNumButton.innerHTML == currentPageNumber) {
			pageNumButton.parentNode.classList.add('active');
			return;
		}
	});
}