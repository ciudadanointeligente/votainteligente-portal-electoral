
$(function(){
    $('.options input[type="checkbox"]:checked').parent().parent().addClass('cat-selected');
    $('.options input[type="checkbox"]').change(function(el){

        let is_selected = $(this).prop("checked");
        let amount_of_selected = $('.options input[type="checkbox"]:checked').length;
        if((amount_of_selected > 3) && is_selected) {
            $(this).prop("checked", false);
            return;
        }
        $(this).parent().parent().removeClass('cat-selected cat-unselected');
        if(is_selected){
            $(this).parent().parent().addClass('cat-selected');
        }
        else{
            $(this).parent().parent().addClass('cat-unselected');
        }
       
    });

});
$(function(){

    let $element = $('.radio input[type="radio"]')
    let $checked = $('.radio input[type="radio"]:checked')

    $checked.parent().parent().addClass('option-selected');

    $element.click(function() {
        $(this).parent().parent().addClass("option-selected");
        $(this).parent().parent().siblings().removeClass("option-selected");
    });

});

$(function() {

    let $tabs_menu = $(".tabs-menu a")

    $tabs_menu.click(function() {
        $(this).parent().addClass("current");
        $(this).parent().siblings().removeClass("current"); 
        
        let tab = $(this).attr("href");
        $(".tab-content").not(tab).css("display", "none");
        $(tab).fadeIn();
    });
});

$(function(){
    $('form.pautas_candidatos').submit(function(event){
      let checkboxes = $('form input[type=checkbox]');
      if (checkboxes.length > 0){
        if (checkboxes.filter(":checked").length !== 3){
          $('.numero_de_temas').effect('highlight',{'color': '#EF476F'},3000); 
          return false;  
        }
        
      }
    });

});
$(function(){

    let $element = $('.radio input[type="radio"]')
    let $checked = $('.radio input[type="radio"]:checked')

    $checked.parent().parent().addClass('option-selected');

    $element.click(function() {
        $(this).parent().parent().addClass("option-selected");
        $(this).parent().parent().siblings().removeClass("option-selected");
    });

});

$(function() {

    let $tabs_menu = $(".tabs-menu a")

    $tabs_menu.click(function() {
        $(this).parent().addClass("current");
        $(this).parent().siblings().removeClass("current"); 
        
        let tab = $(this).attr("href");
        $(".tab-content").not(tab).css("display", "none");
        $(tab).fadeIn();
    });
});
