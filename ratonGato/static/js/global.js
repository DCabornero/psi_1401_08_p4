/*

November Template

http://www.templatemo.com/tm-473-november

*/

/* onScroll function
----------------------------------------*/
// function onScroll(event){
//   var scrollPosition = $(document).scrollTop();
//   $('nav li a').each(function () {
//     var currentLink = $(this);
//     var refElement = $(currentLink.attr("href"));
//     if (refElement.position().top <= scrollPosition && refElement.position().top + refElement.height() > scrollPosition) {
//       $('nav ul li').removeClass("active");
//       currentLink.parent().addClass("active");
//     }
//     else{
//       currentLink.parent().removeClass("active");
//     }
//   });
// }

/* HTML Document is loaded and DOM is ready.
--------------------------------------------*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


$(document).ready(function(){
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
  });

  //mobilemenu
  $('.mobile').click(function(){
    var $self = $(this);
    $('.menumobile').slideToggle( function(){
      $self.toggleClass('closed');
    });
  });

  //navigation script
  $('.Navigation ul li a').click(function(){
    $('.menumobile').removeAttr("style");
    $('#mobile_sec .mobile').removeClass("closed");
  });

  $('a.slicknav_btn').click(function(){
    $(".mobilemenu ul").css({"display":"block"});
  });

  //tab
  $(".tabLink").each(function(){
    $(this).click(function(){
      tabeId = $(this).attr('id');
      $(".tabLink").removeClass("activeLink");
      $(this).addClass("activeLink");
      $(".tabcontent").addClass("hide");
      $("#"+tabeId+"-1").removeClass("hide");
      return false;
    });
  });
  $('a[href*=#]:not([href=#])').click(function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'')
      || location.hostname == this.hostname)
    {
      var target = $(this.hash),
      headerHeight = $(".primary-header").height() + 5; // Get fixed header height
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
      if (target.length)
      {
        $('html,body').animate({
          scrollTop: target.offset().top + 2
        }, 600);
        return false;
      }
    }
  });
  $('.draggable').draggable({
    revert: true,
    containment: "#chess_board"
  });
  $('.droppable').droppable(
    // drop: function(event){
    //   console.log($(this).attr('id'));
  );
  $('#prevbutton').click(function(){
    $.ajax({
      url: '/get_move/',
      method: 'POST',
      data: {
        'shift': -1
      },
      dataType: 'json',
      success: function (data){
        var previmg = $('#cell_'.concat(data['origin'].toString())).html();
        $('#cell_'.concat(data['origin'].toString())).html('');
        $('#cell_'.concat(data['target'].toString())).html(previmg);
        if(!(data['previous'])){
          $("#prevbutton").attr("diabled", true);
        }
        $("#nextbutton").attr("diabled", false);
      }
    })
  });

  $('#nextbutton').click(function(){
    $.ajax({
      url: '/get_move/',
      method: 'POST',
      data: {
        'shift': 1
      },
      dataType: 'json',
      success: function (data){
        var previmg = $('#cell_'.concat(data['origin'].toString())).html();
        $('#cell_'.concat(data['origin'].toString())).html('');
        $('#cell_'.concat(data['target'].toString())).html(previmg);
        if(!(data['next'])){
          $("#nextbutton").attr("diabled", true);
        }
        $("#prevbutton").attr("diabled", false);
      }
    })
  });
  //Header Small
  window.addEventListener('scroll', function(e){
    var distanceY = window.pageYOffset || document.documentElement.scrollTop,
    shrinkOn = 0;

    if (distanceY > shrinkOn) {
      $('header').addClass("smaller");
    } else {
      $('header').toggleClass("smaller");
    }
  });
});



//$(document).on("scroll", onScroll);

// Complete page is fully loaded, including all frames, objects and images
$(window).load(function() {
  // Remove preloader
  // https://ihatetomatoes.net/create-custom-preloading-screen/
  $('body').addClass('loaded');
});
