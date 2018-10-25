$(function() {
    let $encontrei = $(".resultado .options a")

    $encontrei.click(function() {
        let content = $(this).attr("href");
        $(".encontrei-1").not(content).css("display", "none");
        $(content).fadeIn();
    });
});

$(function() {
    let $nao_encontrei = $(".resultado .options a")

    $nao_encontrei.click(function() {
        let content = $(this).attr("href");
        $(".nao-encontrei-1").not(content).css("display", "none");
        $(content).fadeIn();
    });
});

$(function() {
    let $mandei = $(".btn-mandei")

    $mandei.click(function() {
        let content = $(this).attr("href");
        $(".mandei-content").not(content).css("display", "none");
        $(content).fadeIn();
    });
});
