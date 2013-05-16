
/* Toolbar */

function toolbarHide() {
    $('.menuitem > .menu:visible').hide().prev('a').removeClass('active');
}

$window.on('keyup', function (e) {
    if (e.which != 27)
        return;

    toolbarHide(e);
});

$document.on('click', '[data-menuitem] a', function (e) {
    var $item = $(this),
        $menu = $item.next('.menu');

    if ($menu.length === 0)
        return;

    e.preventDefault();

    $item.toggleClass('active');
    $menu.toggle();
});

$document.on('mousedown', function (e) {
    if ($(e.target).closest('.menu').length > 0)
        return;

    toolbarHide(e);
});

$('[data-menuitem] > .menu').addClass('active').hide();
