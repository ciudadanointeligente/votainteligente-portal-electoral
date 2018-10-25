$(document).ready(function() {
  $(".set > .accordion-header").on("click", function() {
    if ($(this).hasClass("active")) {
    $(this).removeClass("active");
    $(this)
      .siblings(".card-body")
      .slideUp(200);
    } else {
    $(".set > .accordion-header").removeClass("active");
    $(this).addClass("active");
    $(".card-body").slideUp(200);
    $(this)
      .siblings(".card-body")
      .slideDown(200);
    }
  });
});
