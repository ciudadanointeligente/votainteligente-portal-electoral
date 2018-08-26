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
    let $not_checked = $('.radio input[type="radio"]:not(:checked)')

    $checked.parent().parent().addClass('option-selected');
    $not_checked.parent().parent().addClass('option-unselected');

});
