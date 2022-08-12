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
        form_data.append("split_by_numbers", $('select[name=split_by_numbers]', $modal).val());
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
                        } else if (json[i][field]) {
                            s += '<td>' + json[i][field] + '</td>';
                        } else {
                            s += '<td>&nbsp;</td>';
                        }
                    });
                    s += '</tr>';
                    $('tbody', $table).prepend($(s));
                }
            }
        });
    }
}


function create_and_upload_blank_numbers(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var second_offset = taiwan_einvoice_site.get_second_offset_by_timezone_id_value(taiwan_einvoice_site);
        var turnkey_web__seller__legal_entity__identifier = $('select[name=turnkey_web__seller__legal_entity__identifier]').val();
        var date_in_year_month_range = $('input[name=date_in_year_month_range]').val();
        var date_in_year_month_range = taiwan_einvoice_site.convert_time_from_utc_str(date_in_year_month_range,
                                                                                      -1 * second_offset,
                                                                                      taiwan_einvoice_site.django_datetime_format);
        var ids = [];
        var $first_tr;
        $('table.search_result tr').each(function(){
            var $tr = $(this);
            var id = $tr.attr('sellerinvoicetrackno_id');
            if (id) {
                ids.push(id);
                $first_tr = $tr;
            }
        });
        if (0 >= ids.length) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$ERROR_MODAL,
                gettext("Data Error"),
                gettext("No data")
            );
            return false;
        }
        $.ajax({
            type: "POST",
            url: $first_tr.attr("resource_uri") + $btn.attr('action') + '/',
            data: JSON.stringify({"turnkey_web__seller__legal_entity__identifier": turnkey_web__seller__legal_entity__identifier,
                   "date_in_year_month_range": date_in_year_month_range,
                   "seller_invoice_track_no_ids": ids.join(",")
                  }),
            dataType: 'json',
            contentType: 'application/json',
            error: function (jqXHR, exception) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$ERROR_MODAL,
                    jqXHR['responseJSON']['error_title'],
                    jqXHR['responseJSON']['error_message'],
                );
            },
            success: function(json) {
                var fmts = ngettext('Create %(count)s record', 'Create %(count)s records', json["slugs"].length);
                var message = interpolate(fmts, { count: json["slugs"].length }, true);
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Create the Blank Number Record Successfully"),
                    message
                );
            }
        });
    }
}


function delete_seller_invoice_track_no_modal (taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $('#delete_seller_invoice_track_no_modal');
        var $modal_table = $('table.modal_table', $modal);
        var $tr = $btn.parents('tr');
        var $tr_clone = $tr.clone();
        $('td[field="button"]', $tr_clone).remove();
        $('tbody tr', $modal_table).remove();
        $('tbody', $modal_table).append($tr_clone);

        $('thead tr', $modal_table).remove();
        var $search_result_head_tr_clone = $('table.search_result thead tr:first').clone();
        $('th[field="button"]', $search_result_head_tr_clone).remove();
        $('thead', $modal_table).append($search_result_head_tr_clone);
        $modal.modal('show');
    }
}


function delete_seller_invoice_track_no (taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var $modal_table = $('table.modal_table', $modal);
        var resource_uri = $('tbody tr:first', $modal_table).attr('resource_uri');
        $.ajax({
            url: resource_uri,
            type: "DELETE",
            dataType: 'json',
            contentType: 'application/json',
            error: function (jqXHR, exception) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$ERROR_MODAL,
                    jqXHR['responseJSON']['error_title'],
                    jqXHR['responseJSON']['error_message'],
                );
            },
            success: function (json) {
                $modal.modal('hide');
                $('tr[resource_uri="'+resource_uri+'"]').remove();
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
    $('button.create_and_upload_blank_numbers').click(create_and_upload_blank_numbers(taiwan_einvoice_site));
    $('button.delete_seller_invoice_track_no_modal').click(delete_seller_invoice_track_no_modal(taiwan_einvoice_site));
    $('button.delete_seller_invoice_track_no').click(delete_seller_invoice_track_no(taiwan_einvoice_site));
});