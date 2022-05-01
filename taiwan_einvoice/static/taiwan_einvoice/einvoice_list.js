function delay_set_up_the_escpos_printer(button_id, modal_id, ws_escposweb_status_url) {
    var d = new Date();
    console.log(d + ': Execute delay_set_up_the_escpos_printer');
    var $button = $('#' + button_id);
    var $modal = $('#' + modal_id);
    return set_up_the_escpos_printer(window.taiwan_einvoice_site, $button, $modal, ws_escposweb_status_url);
};


function show_einvoice_modal(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $tr = $btn.parents('tr');
        if (0 < $tr.length) {
            var einvoice_id = $tr.attr('einvoice_id');
        } else {
            var einvoice_id = $btn.attr('einvoice_id');
        }
        var track_no_ = $btn.text();
        var $modal = $('#show_einvoice_modal');
        $('[field=details_content]', $modal).text('');
        var resource_uri = $modal.attr('resource_uri_tmpl').replace('{id}', einvoice_id);
        var fmts = ngettext('E-Invoice: %(track_no_)s', 'E-Invoice: %(track_no_)s', 1);
        var message = interpolate(fmts, { track_no_: track_no_ }, true);
        $('#show_einvoice_modal_label', $modal).text(message);
        $.ajax({
            url: resource_uri,
            type: "GET",
            dataType: 'json',
            contentType: 'application/json',
            success: function (json) {
                var $modal_body = $('.modal-body', $modal);
                $('span[field!=""]', $modal_body).each(function(){
                    var $span = $(this);
                    var field = $span.attr('field');
                    if ($span.hasClass('datetime')) {
                        var value = $('td[field="'+field+'"]', $tr).attr('value');
                    } else {
                        var value = $('td[field="'+field+'"]', $tr).text();
                    }
                    if (field == 'print_mark') {
                        if (json[field]) {
                            value = pgettext('taiwan_einvoice_print_mark', 'Yes');
                            $('.re_print_einvoice_modal', $modal).show();
                        } else {
                            value = '';
                            $('.re_print_einvoice_modal', $modal).hide();
                        }
                    } else if (field == 'donate_mark') {
                        if ('1' == json[field]) {
                            value = pgettext('taiwan_einvoice_donate_mark', 'Donated');
                        } else {
                            value = '';
                        }
                    } else if (field == 'is_canceled') {
                        if (json[field]) {
                            value = pgettext('taiwan_einvoice_donate_mark', 'Canceled');
                            $('.re_print_einvoice_modal', $modal).hide();
                        } else {
                            value = '';
                        }
                    } else if (field == 'carrier_id2') {
                        if (json['carrier_id1'] == json[field]) {
                            value = '';
                        } else {
                            value = json[field];
                        }
                    } else if (!value && json[field]) {
                        value = json[field];
                    }
                    if (!value) {
                        value = '';
                    }
                    $span.attr('value', value).text(value);
                });
                $('.datetime', $modal_body).each(taiwan_einvoice_site.convert_class_datetime(taiwan_einvoice_site));
                $('[field=related_einvoices] button', $modal_body).remove();
                $('.related_einvoices_div', $modal_body).hide();
                for (var j=0; j<json['related_einvoices'].length; j++) {
                    $('.related_einvoices_div', $modal_body).show();
                    var re = json['related_einvoices'][j];
                    var s = '<button class="btn btn-sm btn-primary show_einvoice_modal" einvoice_id="'+re['id']+'">'+re['track_no_']+'</button>';
                    $('[field=related_einvoices]', $modal_body).append($(s));
                }
                $('button.show_einvoice_modal', $modal_body).click(show_einvoice_modal(taiwan_einvoice_site));
                for (var i=0; i<json['details_content'].length; i++) {
                    if ('text' != json['details_content'][i]['type']) {
                        continue;
                    }
                    var line = json['details_content'][i];
                    $('div[field=details_content]', $modal_body).append(
                        $("<pre>"+line['text']+"</pre>")
                    );
                }
                $modal.data('einvoice_id', einvoice_id);
                $modal.modal('show');
            }
        });
    };
};


function re_print_einvoice_modal(taiwan_einvoice_site) {
    return function () {
        var $status_button = $('#print_einvoice_modal_button_0');
        if (0 >= $('img.status-on:visible', $status_button).length) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNING_MODAL,
                pgettext('taiwan_einvoice', 'Error'),
                gettext('It can not connect ESC/POS Printer Server'));
            return false;
        }
        var $btn = $(this);
        var $from_modal = $btn.parents('.modal');
        var $modal = $('#re_print_einvoice_modal');
        $modal.data("einvoice_id", $from_modal.data('einvoice_id'));
        $modal.modal('show');
    };
};


function re_print_einvoice_sure_modal(taiwan_einvoice_site) {
    return function () {
        var $status_button = $('#print_einvoice_modal_button_0');
        var escposweb_id_name = $.cookie.get(taiwan_einvoice_site.default_escposweb_cookie_name);
        if (0 >= $('img.status-on:visible', $status_button).length) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNING_MODAL,
                pgettext('taiwan_einvoice', 'Error'),
                gettext('It can not connect ESC/POS Printer Server'));
            return false;
        } else if (!escposweb_id_name) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNING_MODAL,
                pgettext('taiwan_einvoice', 'Error'),
                gettext('It can not connect ESC/POS Printer Server'));
            return false;
        }
        var escposweb_id = escposweb_id_name.split(':')[0];
        var $btn = $(this);
        var $from_modal = $btn.parents('.modal');
        var einvoice_id = $from_modal.data("einvoice_id");
        var reason = $('textarea[name=reason]', $from_modal).val();
        if (!reason && reason.length < 10) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNING_MODAL,
                pgettext('taiwan_einvoice', 'Error'),
                gettext('Reason must has more than 10 words.'));
            $('textarea[name=reason]', $from_modal).focus();
            return false;
        }
        var $modal = $('#re_print_einvoice_sure_modal');
        $('[field=reason]', $modal).text(reason);
        $modal.data('einvoice_id', einvoice_id);
        $('[name=reason]', $from_modal).val('');

        var $einvoice_printer_select = $('[name=einvoice_printer]', $modal);
        $('option', $einvoice_printer_select).remove();
        $('#print_einvoice_modal select[name=einvoice_printer] option').each(function(){
            var value = $(this).attr('value');
            var selected = $(this).prop('selected');
            var text = $(this).text();
            $einvoice_printer_select.append($('<option value="'+value+'" selected="'+selected+'">'+text+'</option>'));
        });
        $einvoice_printer_select.val($('#print_einvoice_modal select[name=einvoice_printer]').val());
        var $details_printer_select = $('[name=details_printer]', $modal);
        $('option', $details_printer_select).remove();
        $('#print_einvoice_modal select[name=details_printer] option').each(function(){
            var value = $(this).attr('value');
            var selected = $(this).prop('selected');
            var text = $(this).text();
            $details_printer_select.append($('<option value="'+value+'" selected="'+selected+'">'+text+'</option>'));
        });
        $details_printer_select.val($('#print_einvoice_modal select[name=details_printer]').val());

        var $table = $('table.search_result');
        var $modal_table = $('table', $modal);
        $('tbody tr.data', $modal_table).remove();
        var no = 1;
        $('tr[einvoice_id='+einvoice_id+']', $table).each(function () {
            var $tr = $(this);
            var $tr_tmpl = $('tr.tr_tmpl', $modal_table).clone().removeClass('tr_tmpl').addClass('data');
            $tr_tmpl.attr('einvoice_id', einvoice_id);
            $('td[field=no]', $tr_tmpl).text(no);
            var keys = [];
            $('td', $tr_tmpl).each(function () {
                var field = $(this).attr('field');
                if (field && field != 'no') {
                    keys.push(field);
                }
            })
            for (var i = 0; i < keys.length; i++) {
                var t = $('td[field=' + keys[i] + ']', $tr).text();
                $('td[field=' + keys[i] + ']', $tr_tmpl).attr('value', t).text(t);
            }
            $tr_tmpl.show().appendTo($('tbody', $modal_table));
            no += 1;
        });

        var $_b = $('#print_einvoice_modal_button_0');
        var ws_escposweb_url= $_b.attr('ws_escposweb_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_print_result_url= $_b.attr('ws_escposweb_print_result_url_tmpl').replace('{id}', escposweb_id);

        var $print_mark_td = $('td[field=print_mark]', $modal_table);
        $print_mark_td.text('');
        var $re_print_original_copy = $('<button class="btn btn-info re_print_original_copy" id="re_print_einvoice_with_reason_button_0" click_once="true">' + gettext('Re-print original copy') + '</button>');
        $re_print_original_copy.click(print_einvoice(taiwan_einvoice_site,
                                                     ws_escposweb_url,
                                                     ws_escposweb_print_result_url));
        $print_mark_td.append($re_print_original_copy);

        $from_modal.modal('hide');
        $('select, input', $modal).prop('disabled', false);
        $modal.modal('show');
    };
};


$(function () {
    $(".nav_einvoice").addClass("nav_active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();
    window.taiwan_einvoice_site = taiwan_einvoice_site;

    adjust_pagination_html();

    $('select[name=einvoice_printer').change(function () {
        var value = $(this).val();
        Cookies.set(taiwan_einvoice_site.default_einvoice_printer_cookie_name, value, { path: '/' });
    });
    $('select[name=details_printer').change(function () {
        var value = $(this).val();
        Cookies.set(taiwan_einvoice_site.default_details_printer_cookie_name, value, { path: '/' });
    });
    $('input[name=append_to_einvoice').click(function () {
        var value = $(this).prop('checked');
        Cookies.set(taiwan_einvoice_site.default_append_to_einvoice_cookie_name, value, { path: '/' });
    });
    $('select[name=interval_seconds_of_printing').change(function () {
        var value = $(this).val();
        Cookies.set(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name, value, { path: '/' });
    });
    if ('true' == Cookies.get(taiwan_einvoice_site.default_append_to_einvoice_cookie_name)) {
        $('input[name=append_to_einvoice').prop('checked', 'checked');
    }
    if (Cookies.get(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name)) {
        $('select[name=interval_seconds_of_printing').val(Cookies.get(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name));
    }
    var escposweb_cookie_name = taiwan_einvoice_site.default_escposweb_cookie_name;
    var pass_key_name = escposweb_cookie_name + '_pass_key';
    var escposweb_id_name = $.cookie.get(escposweb_cookie_name);
    var pass_key = $.cookie.get(pass_key_name);
    if (escposweb_id_name) {
        var escposweb_id = escposweb_id_name.split(':')[0];
        var escposweb_name = escposweb_id_name.split(':')[1].replace(/%3A/g, ':');
        var $btn = $('button.print_einvoice_modal');
        var ws_escposweb_status_url = $btn.attr('ws_escposweb_status_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_url = $btn.attr('ws_escposweb_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_print_result_url = $btn.attr('ws_escposweb_print_result_url_tmpl').replace('{id}', escposweb_id);
        var fmts = ngettext('%(escposweb_name)s - Pass Key: %(pass_key)s', '%(escposweb_name)s(Pass Key: %(pass_key)s)', 1);
        var button_text = interpolate(fmts, {escposweb_name: escposweb_name, pass_key: pass_key}, true);
        $('span#default_escpos_print_name', $btn).text(button_text);
        var $table = $('table.search_result');
        var $modal = $('#print_einvoice_modal');
        $modal.data({
            ws_escposweb_status_url: ws_escposweb_status_url,
            ws_escposweb_url: ws_escposweb_url,
            ws_escposweb_print_result_url: ws_escposweb_print_result_url
        });
        var $print_einvoice_button = $('.print_einvoice', $modal);
        $print_einvoice_button.click(print_einvoice(taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_result_url));
        $btn.removeClass('btn-danger').addClass('btn-secondary').click(function () {
            var $b = $(this);
            $('button.print_einvoice', $modal).show();
            $('select, input', $modal).removeAttr("disabled");
            if (0 >= $('img.status-on:visible', $b).length) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNING_MODAL,
                    pgettext('taiwan_einvoice', 'Error'),
                    gettext('It can not connect ESC/POS Printer Server'));
                return false;
            } else if ($('input[name=print_einvoice]:checked', $table).length == 0) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNING_MODAL,
                    pgettext('taiwan_einvoice', 'WARNING'),
                    gettext('Please choose one record at least'));
                return false;
            }
            var $modal_table = $('table', $modal);
            $('tbody tr.data', $modal_table).remove();
            var no = 1;
            $('input[name=print_einvoice]:checked', $table).each(function () {
                var $i = $(this);
                var $tr = $i.parents('tr');
                var $tr_tmpl = $('tr.tr_tmpl', $modal_table).clone().removeClass('tr_tmpl').addClass('data');
                $tr_tmpl.attr('einvoice_id', $tr.attr('einvoice_id'));
                $('td[field=no]', $tr_tmpl).text(no);
                var keys = [];
                $('td', $tr_tmpl).each(function () {
                    var field = $(this).attr('field');
                    if (field && field != 'no') {
                        keys.push(field);
                    }
                })
                for (var i = 0; i < keys.length; i++) {
                    var t = $('td[field=' + keys[i] + ']', $tr).text();
                    $('td[field=' + keys[i] + ']', $tr_tmpl).attr('value', t).text(t);
                }
                $('tbody', $modal_table).prepend($tr_tmpl.show());
                no += 1;
            });
            $modal.modal('show');
        });
        check_receive_escpos_printer_status_timestamp();
        set_up_the_escpos_printer(taiwan_einvoice_site, $btn, $modal, ws_escposweb_status_url);
    } else {
        $('button.print_einvoice_modal').removeClass('btn-secondary').addClass('btn-danger'
        ).text(gettext("Set up 'Default ESC/POS Printer first'")).click(function () {
            window.location = $(this).attr('set_up_default_escpos_printer_url');
        });
    }

    $('button.suspend_print_einvoice').click(suspend_print_einvoice(taiwan_einvoice_site));
    $('button.show_einvoice_modal').click(show_einvoice_modal(taiwan_einvoice_site));
    $('button.re_print_einvoice_modal').click(re_print_einvoice_modal(taiwan_einvoice_site));
    $('button.re_print_einvoice_sure_modal').click(re_print_einvoice_sure_modal(taiwan_einvoice_site));
    if (ws_escposweb_url && ws_escposweb_status_url) {
        $('button#print_einvoice_button_1').click(print_einvoice(taiwan_einvoice_site,
                                                                 ws_escposweb_url,
                                                                 ws_escposweb_print_result_url));
    }
});