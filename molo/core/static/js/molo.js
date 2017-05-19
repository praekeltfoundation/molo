
"use strict";

var domReady = function(callback) {
  document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
};

var hidePagination = function() {
  document.body.classList.add('toggle-hide');
}


var loadMore = function() {
  var moreLink = document.getElementById('more-link');
  
  if (moreLink) {
    var articlesMore = document.getElementById('articles-more');
    
    if (articlesMore === null) {
      var wrapper = document.createElement('div');
      moreLink.parentNode.insertBefore(wrapper, moreLink);
      wrapper.appendChild(moreLink);
      wrapper.setAttribute("id", "articles-more");
    };
    
    wrapper.addEventListener("click", function(event){
      var element = event.target;
      if (element.tagName == 'A' && element.classList.contains("more-link")) {
        event.preventDefault();
        element.innerHTML = 'Loading...'
        fetch(element.getAttribute('data-next'))
         .then(function(response) {
           return response.text();
         }).then(function(text) {
           element.parentNode.insertAdjacentHTML('beforeend', text);
           element.parentNode.removeChild(element);
        });
       }
    });
  }
  
};

domReady(function() {
  loadMore();
  hidePagination();
});

