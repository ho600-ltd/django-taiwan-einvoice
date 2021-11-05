function upload_csv_to_multiple_create_modal (taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $('#upload_csv_to_multiple_create_modal');
        $modal.modal('show');
    }
}


function upload_csv_to_multiple_create(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var csrfmiddlewaretoken = $('input[name=csrfmiddlewaretoken]:first').val();
        var form_data = '';
        form_data = new FormData();
        form_data.append("turnkey_web", $('select[name=turnkey_web]', $modal).val());
        var file = $('input[type=file]', $modal)[0].files[0];
        if (! file) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNING_MODAL,
                gettext('File Error'),
                gettext('Please choose .csv')
            );
            return false;
        }
        form_data.append("file", file);
        $.ajax({
            type: "POST",
            url: $modal.attr('resource_uri'),
            cache: false, 
            contentType: false, 
            processData: false,
            async: true,
            headers: {"X-CSRFToken": csrfmiddlewaretoken},
            data: form_data,
            error: function (jqXHR, exception) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$ERROR_MODAL,
                    jqXHR['responseJSON']['error_title'],
                    jqXHR['responseJSON']['error_message'],
                );
            },
            success: function(json) {
                $('input[type=file]', $modal).val('');
                $modal.modal('hide');

                var fmts = ngettext('import %(count)s record', 'import %(count)s records', json.length);
                var message = interpolate(fmts, { count: json.length }, true);
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Importing Successfully"),
                    message
                );
                var $table = $('table.search_result');
                for (var i=0; i<json.length; i++) {
                    var s = '<tr>';
                    $('thead tr th', $table).each(function(){
                        var $th = $(this);
                        var field = $th.attr('field');
                        if ('no' == field) {
                            s += '<td>' + gettext('NEW Record') + '</td>';
                        } else if ('turnkey_web' == field) {
                            s += '<td>' + json[i]['turnkey_web_dict']['name'] + '</td>';
                        } else {
                            s += '<td>' + json[i][field] + '</td>';
                        }
                    });
                    s += '</tr>';
                    $('tbody', $table).prepend($(s));
                }
            }
        });
    }
}


$(function () {
    $(".nav_sellerinvoicetrackno").addClass("nav_active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal'),
    });

    taiwan_einvoice_site.after_document_ready();

    adjust_pagination_html();

    $('button.upload_csv_to_multiple_create_modal').click(upload_csv_to_multiple_create_modal(taiwan_einvoice_site));
    $('button.upload_csv_to_multiple_create').click(upload_csv_to_multiple_create(taiwan_einvoice_site));
});