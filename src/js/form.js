
/* Form */

var FORM_EDITED = false;

// Focus on first autofocus field
$('[autofocus]:first').select();

// Handle window close if needed
var $input = $(':input[name=data]').on('change', function () {
    if (!FORM_EDITED)
        FORM_EDITED = true;
});

if ($input.length > 0) {
    $window.on('beforeunload', function (e) {
        if (FORM_EDITED)
            e.preventDefault();
    });

    if ($input.attr('type') == 'hidden')
        FORM_EDITED = true;

    $input.closest('form').on('submit', function () {
        $window.off('beforeunload');
    });
}
