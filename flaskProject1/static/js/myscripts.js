$(".target").on("click", function() {
    let $button = $(this);
    let oldVal = parseInt($button.parent().find("input").val());
    let newVal = 0;

    if ($button.text() == '+') {
        newVal = oldVal + 1;
    }

    else {
        if (oldVal > 0) {
            newVal = oldVal - 1;
        }
        else {
            newVal = 0;
        }
    }

    $button.parent().find("input").val(newVal);
});


$(".spansize").on("click", function() {
    var spanText = $(this).text();
    console.log(spanText);
    $(this).siblings("input").val(spanText);
    $('.spansize').removeClass('spanactive'); // 移除所有 span 的 active class
    $(this).addClass('spanactive'); // 添加当前点击的 span 的 active class
    // $button.parent().find("input").val(newVal);
});


$('.addToCart').on("click", function(event) {
    console.log('hello');
    if($(this).prev().prev().find("input").val() == '') {
        event.preventDefault();
        $(this).next().next().next().html("You need to select the size.");
        $(this).next().next().next().css("display", "block");
        $(this).next().next().next().delay(3000).slideUp();
        return false
    }
    if($(this).prev().prev().prev().prev().find("input").val() == '0') {
        event.preventDefault();
        $(this).next().next().next().html("You need to select at least one shirt.");
        $(this).next().next().next().css("display", "block");
        $(this).next().next().next().delay(3000).slideUp();
        return false
    }

    if ($(this).prev().val() == "0") {
        event.preventDefault();
        $(this).next().next().next().html("You need to log in to buy.");
        $(this).next().next().next().css("display", "block");
        $(this).next().next().next().delay(3000).slideUp();
        return false
    }
});
console.log('hi')

$(".flashMessage").delay(3000).slideUp();

