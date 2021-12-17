var rootElement = document.documentElement;

function scrollToTop() {
    // Source: https://css-tricks.com/how-to-make-an-unobtrusive-scroll-to-top-button/

    // Scroll to top logic
    rootElement.scrollTo({
      top: 0,
      behavior: "smooth"
    })
  }

var scrollToTopBtn = document.getElementById("scrollToTopBtn");

// JS hide "Back to top" button if scroll bar is present, but show otherwise (default)
$(document).ready(function() {
    // Check if body height is higher than window height :)
    if ($("body").height() < $(window).height()) {
        $("#scrollToTopBtn").css('display', 'none');
    }
});
