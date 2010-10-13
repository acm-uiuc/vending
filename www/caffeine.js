function updatePage(page) {
	$.ajaxError(displayError);
	$.get("/" + page, {}, rewritePage, "html");
}

function rewritePage(newPage, status, requestObject) {
	content = $("#content");
	content.animate({left: 0},,,function() {
			content.empty();
			content.html(newPage);
			content.animate({left: content.outerWidth()});
		});
}

function displayError(requestObject, status, error) {
	$("#content").prepend("<b>We done goofed</b><br /><p>" + status + " -- " + error + "</p>");
}
