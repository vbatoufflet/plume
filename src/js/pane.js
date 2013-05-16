
/* Pane */

$document.on('click', '[data-menuitem=fold] a', function (e) {
    var $item = $(this);

    e.preventDefault();

    $pane.toggleClass('folded');
    $view.toggleClass('full');

    $item.attr('data-icon', $pane.hasClass('folded') ? 'right' : 'left');
    $.cookie('pane-folded', $pane.hasClass('folded'));
});

if ($.cookie('pane-folded') == 'true' && $pane.find('.content .msgwarn, .content .msginfo').length === 0)
    $('[data-menuitem=fold] a').trigger('click');
