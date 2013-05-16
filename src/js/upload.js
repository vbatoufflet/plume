
/* Upload */

$('input[type=file]').each(function () {
    $('[data-fileinput=' + this.name + '] input').on('click', function (e) {
        if (e.which != 1)
            return;

        var $file_input = $('input[type=file][name=' + $(this).closest('[data-fileinput]').
            attr('data-fileinput') + ']');

        if (this.type != 'submit' || this.type == 'submit' && !$file_input.val()) {
            $file_input.trigger('click');
            e.preventDefault();
        }
    });

    $(this).on('change', function () {
        $('[data-fileinput=' + this.name + '] input[type=text]').val(this.value);
    }).hide();
});
