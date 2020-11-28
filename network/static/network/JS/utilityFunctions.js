/* UTILITY FUNCTIONS */
function getCookie(name) {
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');

		for (let i = 0; i < cookies.length; i++) {
			let cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				var cookieValue = null;
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function convertPythonBooleanToJsBoolean(input) {
	try {
		if (input === 'False')
			return false;
		else if (input === 'True')
			return true;
		else
			throw 'Invalid argument';
	} catch(err) {
		console.log(`Error: ${err}`);
	}
}