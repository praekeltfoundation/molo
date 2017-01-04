"use strict";
(function() {

  $(document).ready(function(){
    var initialDivPostion = $('.main_wrapper').offset().top;
      $(window).scroll(function() {
        var currentScrollPosition = $(window).scrollTop();
    		if(currentScrollPosition > 445) {
          $('.sidebar').css({
            position: 'fixed',
            top: '175px'
          });
        } else {
          $('.sidebar').css({
            position: 'inherit'
          });
        }
      });
  });

})();
