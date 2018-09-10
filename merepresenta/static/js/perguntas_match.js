
$(function(){
    $('.options input[type="checkbox"]:checked').parent().parent().addClass('cat-selected');
    $('.options input[type="checkbox"]').change(function(el){

        let is_selected = $(this).prop("checked");
        let amount_of_selected = $('.options input[type="checkbox"]:checked').length;
        
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