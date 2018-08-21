$(function(){
    var currentDate = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
    $("#nascimento-id").datepicker({
        format: 'dd/mm/yyyy'
    });
});
