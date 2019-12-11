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
var timeoutRet = null;
var timeoutUpdate = null;
var flag = 0;
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

function nextb(){
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
      if(data['next'] != true){
        $("#nextbutton").attr("disabled", true);
        $("#autoplay").attr("disabled", true);
        if(timeoutRet != null){
          clearInterval(timeoutRet);
          timeoutRet = null;
          flag = 0;
        }
      }
      $("#prevbutton").attr("disabled", false);
    }
  })}

function updateGame(){
  $.ajax({
    url: '/current_move/',
    method: 'POST',
    success: function (data){
      var waiting_for_mouse = $("blockquote[class='cat']").text().includes("Waiting")
      var waiting_for_cat = $("blockquote[class='mouse']").text().includes("Waiting")
      var origin = data['origin']
      var target = data['target']
      if(waiting_for_cat && data['last_move'] == 'cat'){
        $("blockquote[class='mouse']").html("");
        var previmg = $('#cell_'.concat(origin.toString())).html();
        $('#cell_'.concat(origin.toString())).html('');
        $('#cell_'.concat(target.toString())).html(previmg);
        $("img[alt='Mouse']").addClass("draggable");
        $(".draggable[alt='Mouse']").draggable({
          revert: true,
          containment: "#chess_board",
          drag: function(){
            $("input[name='origin']").val(parseInt($(this).parent().attr('id').slice(5)));
          }
        }).draggable('enable');
        clearInterval(timeoutUpdate);
        timeoutUpdate = null;
      }
      else if(waiting_for_mouse && data['last_move'] == 'mouse'){
        $("blockquote[class='cat']").html("");
        var previmg = $('#cell_'.concat(origin.toString())).html();
        $('#cell_'.concat(origin.toString())).html('');
        $('#cell_'.concat(target.toString())).html(previmg);
        $("img[alt='Cat']").addClass("draggable");
        $(".draggable[alt='Cat']").draggable({
          revert: true,
          containment: "#chess_board",
          drag: function(){
            $("input[name='origin']").val(parseInt($(this).parent().attr('id').slice(5)));
          }
        }).draggable('enable');
        clearInterval(timeoutUpdate);
        timeoutUpdate = null;
      }
      if(data['winner'] == 'cat'){
        if(waiting_for_mouse){
          alert("You win!!!!");
        }
        else{
          alert("You lose :(");
        }
        clearInterval(timeoutUpdate);
        timeoutUpdate = null;
      }
      if(data['winner'] == 'mouse'){
        if(waiting_for_cat){
          alert("You win!!!!");
        }
        else{
          alert("You lose :(");
        }
        clearInterval(timeoutUpdate);
        timeoutUpdate = null;
      }
    }
  })
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
    containment: "#chess_board",
    drag: function(){
      $("input[name='origin']").val(parseInt($(this).parent().attr('id').slice(5)));
    }
  });
  $('.droppable').droppable({
    drop: function(){
      $("input[name='target']").val(parseInt($(this).attr('id').slice(5)));
      var origin = $("input[name='origin']").val();
      var target = $("input[name='target']").val();
      $.ajax({
        url: '/move/',
        method: 'POST',
        data: {
          'origin' : origin,
          'target' : target
        },
        dataType: 'json',
        success: function(data){
          if(data['valid'] == 1){
            var previmg = $('#cell_'.concat(origin.toString())).html();
            $('#cell_'.concat(origin.toString())).html('');
            $('#cell_'.concat(target.toString())).html(previmg);
            $('#cell_'.concat(target.toString())).find(".draggable").css("top", "");
            $('#cell_'.concat(target.toString())).find(".draggable").css("left", "");
            if(data['winner'] == "cat"){
              if(previmg.includes("Cat")){
                alert('You win!!!!')
              }
              else{
                alert('You lose :(')
              }
            }
            else if(data['winner'] == "mouse"){
              if(previmg.includes("Cat")){
                alert('You lose :(')
              }
              else{
                alert('You win!!!!')
              }
            }
            else{
              timeoutUpdate = setInterval(updateGame, 4000);
            }
            if(previmg.includes("Cat") && data['winner'] == null){
              $(".draggable[alt='Cat']").draggable().draggable('disable');
              $("blockquote[class='cat']").html("<p>Waiting for the mouse...<a style='margin-left:20px;font-weight:normal' href='javascript:window.location.reload(true)'>Refresh</a></p>")
            }
            else if(previmg.includes("Mouse") && data['winner'] == null){
              $(".draggable[alt='Mouse']").draggable().draggable('disable');
              $("blockquote[class='mouse']").html("<p>Waiting for the cat...<a style='margin-left:20px;font-weight:normal' href='javascript:window.location.reload(true)'>Refresh</a></p>")
            }
            else{
              $("blockquote[class='cat']").html("")
              $("blockquote[class='mouse']").html("")
            }
          }
        }
      })
    }}
  );
  if($("blockquote[class='mouse']").text().includes('Waiting') || $("blockquote[class='cat']").text().includes('Waiting')){
    timeoutUpdate = setInterval(updateGame, 4000);
  }
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
        if(data['previous'] != true){
          $("#prevbutton").attr("disabled", true);
        }
        $("#nextbutton").attr("disabled", false);
        $("#autoplay").attr("disabled", false);
      }
    })
  });

  $('#nextbutton').click(nextb);

  $('#autoplay').click(function(){
    if(flag == 0){
      timeoutRet = setInterval(nextb,2000);
      flag = 1;
    }
    else{
      clearInterval(timeoutRet);
      flag = 0;
    }
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