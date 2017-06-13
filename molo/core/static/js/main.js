"use strict";
(function() {

  $(document).ready(function(){
    //Div Scroll Style
    var initialDivPostion = $('.main_wrapper').offset().top;
      $(window).scroll(function() {
        var currentScrollPosition = $(window).scrollTop();
    		if(currentScrollPosition > 445) {
          $('.sidebar').addClass('stickySidebar');
          $('.sidebar').removeClass('noStickySidebar');
        } else {
          $('.sidebar').addClass('noStickySidebar');
          $('.sidebar').removeClass('stickySidebar');
        }
      });

      //Extra Menu - Active state
      $('.extra-list__menuitem a').click(function() {
        var $this = $(this);

        this.addClass('is-active');
        $('.extra-list__menuitem a').removeClass('is-active');

        $('.content__prk .content').css({
          'padding-top': '117px'
        });
      });
  });

})();
