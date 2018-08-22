$(function () {
$('[data-toggle="tooltip"]').tooltip()
})
$(function(){
  let pass_email = function(event){
    let checkbox = $('input[name=email_previous]:checked');
    let val = checkbox.val()
    if (val != 'outro'){
      $('input[name=email]').val(val);
    }
  }
  $('#form_candidate_profile').submit(pass_email);
});
$(function(){
  let show_lgbt_desc = function(){
    $("#lgbt_desc").show(600);
  }
  let hide_lgbt_desc = function(){
    $("#lgbt_desc").hide(600);
    $('#lgbt_desc input').removeAttr('checked');
  }
  $('#id_lgbt').change(function(evt){
    if($(this).is(':checked')){
      show_lgbt_desc();
    }
    else {
      hide_lgbt_desc();
    }
  })
});
