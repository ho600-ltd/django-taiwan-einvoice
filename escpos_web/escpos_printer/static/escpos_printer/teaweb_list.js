function update_teaweb_modal (escpos_web_site) {
    return function () {
        var $modal = $('#update_teaweb_modal');
        var $btn = $(this);
        var $tr = $btn.parents('tr');
        $('td', $tr).each(function(){
            var $td = $(this);
            var field = $td.attr('field');
            if (field) {
                $('p[field="'+field+'"]', $modal).text($td.text());
            }
        });
        $('input[name=pass_key]', $modal).val('');
        $modal.data('teaweb_id', $tr.attr('obj_id'));
        $modal.modal('show');
    };
};


function update_teaweb (escpos_web_site) {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var $tr = $('table.search_result tr[obj_id="'+$modal.data('teaweb_id')+'"]');
        var resource_uri = $tr.attr('resource_uri');
        var pass_key = $('input[name=pass_key]', $modal).val();
        if (!pass_key) {
            escpos_web_site.show_modal(escpos_web_site.$WARNING_MODAL,
                gettext("Pass Key Error"),
                gettext("Please input the \"Pass Key\".")
            );
            return false;
        }
        var data = {
            now_use: true,
            pass_key: pass_key
        }
        $.ajax({
            url: resource_uri,
            type: "PATCH",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json',
            error: function (jqXHR, exception) {
                escpos_web_site.show_modal(
                    escpos_web_site.$ERROR_MODAL,
                    jqXHR['responseJSON']['error_title'],
                    jqXHR['responseJSON']['error_message'],
                );
            },
            success: function (json) {
                $modal.modal('hide');
                var $tr = $('tr[resource_uri="'+resource_uri+'"]');
                $('[field=now_use]', $('table.search_result')).text('');
                $('[field=now_use]', $tr).html('<i class="far fa-check-circle"></i>');
            }
        });
    };
};


$(function () {
    $(".nav_teaweb").addClass("nav_active");

    escpos_web_site = new ESCPOS_PRINTER_SITE('escpos_web_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    escpos_web_site.after_document_ready();
    window.escpos_web_site = escpos_web_site;

    adjust_pagination_html();

    $('button.update_teaweb_modal').click(update_teaweb_modal(escpos_web_site));
    $('button.update_teaweb').click(update_teaweb(escpos_web_site));
});