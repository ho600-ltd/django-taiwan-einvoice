function delay_set_up_the_escpos_printer (button_id, modal_id, ws_escposweb_status_url) {
    var d = new Date();
    console.log(d + ': Execute delay_set_up_the_escpos_printer');
    var $button = $('#'+button_id);
    var $modal = $('#'+modal_id);
    return set_up_the_escpos_printer(window.taiwan_einvoice_site, $button, $modal, ws_escposweb_status_url);
};


function check_receive_escpos_printer_status_timestamp () {
    var $button = $('button.print_einvoice_modal');
    var d = new Date();
    console.log(d + ': Execute check_receive_escpos_printer_status_timestamp');
    var now = Date.now();
    var $status_on = $('img.status-on', $button)
    var privous_timestamp = $status_on.attr('receive_timestamp');
    var interval_seconds = $status_on.attr('interval_seconds');
    if (privous_timestamp && interval_seconds && now - privous_timestamp >= 2000 * interval_seconds) {
        if (0 >= $('img.status-error:visible', $button).length) {
            $('img.status-off', $button).show();
            $('img.status-error', $button).hide();
            $('img.status-on', $button).hide();
        }
    }
    if (interval_seconds && interval_seconds > 0) {
        setTimeout('check_receive_escpos_printer_status_timestamp()', 4000 * interval_seconds);
    } else {
        setTimeout('check_receive_escpos_printer_status_timestamp()', 10000);
    }
}


function set_up_the_escpos_printer (taiwan_einvoice_site, $button, $modal, ws_escposweb_status_url) {
    const escpos_web_status_socket = new WebSocket(taiwan_einvoice_site.WS_PROTOCOL+ws_escposweb_status_url);
    window.escpos_web_status_socket = escpos_web_status_socket;
    escpos_web_status_socket.onerror = function(e) {
        var d = new Date();
        console.error(d + ': escpos_web_status socket connect fails');
        $('img.status-error', $button).show();
        $('img.status-on', $button).hide();
        $('img.status-off', $button).hide();
        if (!taiwan_einvoice_site.done_show_websocket_connection_error) {
            var seen_websocket_connection_error = Cookies.get("Seen WebSocket Connection Error");
            seen_websocket_connection_error = seen_websocket_connection_error ? parseInt(seen_websocket_connection_error) : 0;
            if (! seen_websocket_connection_error || seen_websocket_connection_error < 3) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNING_MODAL,
                    pgettext('taiwan_einvoice', 'WebSocket Connection Error'),
                    gettext('<p>Could not connect web server with websocket protocol, now.  It will cause printing job, except searching E-Invoice.</p><p>If you need to print E-Invoice, please wait for the successful connection.</p>'));
                Cookies.set("Seen WebSocket Connection Error", seen_websocket_connection_error+1, { path: '/' });
            }
            taiwan_einvoice_site.done_show_websocket_connection_error = true;
        }
        var button_id = $button.attr('id');
        var modal_id = $modal.attr('id');
        setTimeout('delay_set_up_the_escpos_printer("'+button_id+'", "'+modal_id+'", "'+ws_escposweb_status_url+'")', 60000);
    };

    escpos_web_status_socket.onclose = function(e) {
        var d = new Date();
        console.error(d + ': escpos_web_status socket closed unexpectedly');
        if (0 < $('img.status-on:visible', $button).length) {
            $('img.status-off', $button).show();
            $('img.status-error', $button).hide();
            $('img.status-on', $button).hide();
            if (!taiwan_einvoice_site.done_show_websocket_connection_error) {
                var seen_websocket_connection_error = Cookies.get("Seen WebSocket Connection Error");
                seen_websocket_connection_error = seen_websocket_connection_error ? parseInt(seen_websocket_connection_error) : 0;
                if (! seen_websocket_connection_error || seen_websocket_connection_error < 3) {
                    taiwan_einvoice_site.show_modal(
                        taiwan_einvoice_site.$WARNING_MODAL,
                        pgettext('taiwan_einvoice', 'WebSocket Connection Error'),
                        gettext('<p>Could not connect web server with websocket protocol, now.  It will cause printing job, except searching E-Invoice.</p><p>If you need to print E-Invoice, please wait for the successful connection.</p>'));
                    Cookies.set("Seen WebSocket Connection Error", seen_websocket_connection_error+1, { path: '/' });
                }
                taiwan_einvoice_site.done_show_websocket_connection_error = true;
            }
            var button_id = $button.attr('id');
            var modal_id = $modal.attr('id');
            setTimeout('delay_set_up_the_escpos_printer("'+button_id+'", "'+modal_id+'", "'+ws_escposweb_status_url+'")', 5000);
        }
    };

    escpos_web_status_socket.onmessage = function(e) {
        $('img.status-on', $button).show().attr('receive_timestamp', Date.now());
        $('img.status-off', $button).hide();
        $('img.status-error', $button).hide();
        const data = JSON.parse(e.data);
        window.PRINTERS_DATA = data;
        var $einvoice_printer = $('select[name=einvoice_printer]', $modal);
        var einvoice_printer_value = Cookies.get(taiwan_einvoice_site.default_einvoice_printer_cookie_name);
        var $details_printer = $('select[name=details_printer]', $modal);
        var details_printer_value = Cookies.get(taiwan_einvoice_site.default_details_printer_cookie_name);
        $('option', $einvoice_printer).remove();
        $('option', $details_printer).remove();
        for (k in data) {
            if (k == 'interval_seconds') {
                $('img.status-on', $button).attr('interval_seconds', data[k]['value']);
                continue;
            } else if (k == 'error_message') {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNING_MODAL,
                    pgettext('taiwan_einvoice', 'WARNING'),
                    data[k]['value']);
                $('img.status-error', $button).show();
                $('img.status-on', $button).hide();
                $('img.status-off', $button).hide();
                var button_id = $button.attr('id');
                var modal_id = $modal.attr('id');
                setTimeout('delay_set_up_the_escpos_printer("'+button_id+'", "'+modal_id+'", "'+ws_escposweb_status_url+'")', 60000);
                return false;
            }
            const v = data[k]['nickname'] + '(' + data[k]['receipt_type_display'] + ')';
            var $option = $('<option value="'+k+'">'+v+'</option>');
            $details_printer.append($option);
            if ('6' == data[k]['receipt_type']) {
                var $ei_option = $('<option value="'+k+'">'+v+'</option>');
                $einvoice_printer.append($ei_option);
            }
            window.PRINTERS_DATA[k]['width'] = taiwan_einvoice_site.printer_receipt_type_width[data[k]['receipt_type']];
        }
        if(einvoice_printer_value) {
            $('option[value='+einvoice_printer_value+']', $einvoice_printer).attr('selected', 'selected');
        }
        if (details_printer_value) {
            $('option[value='+details_printer_value+']', $details_printer).attr('selected', 'selected');
        }
    };
};


function build_two_websockets(taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_result_url, $button) {
    console.log("ws_escposweb_url: "+ws_escposweb_url);
    console.log("ws_escposweb_print_result_url: "+ws_escposweb_print_result_url);
    var escpos_web_socket = new WebSocket(taiwan_einvoice_site.WS_PROTOCOL+ws_escposweb_url);
    var escpos_web_print_result_socket = new WebSocket(taiwan_einvoice_site.WS_PROTOCOL+ws_escposweb_print_result_url);
    escpos_web_socket.onopen = function(e) {
        $button.attr('escpos_web_socket', true);
        var d = new Date();
        console.log(d + ': escpos_web socket onopen');
    };
    escpos_web_socket.onerror = function(e) {
        $button.attr('escpos_web_socket', false);
        var d = new Date();
        console.log(d + ': escpos_web socket onerror');
    };
    escpos_web_socket.onclose = function(e) {
        $button.attr('escpos_web_socket', false);
        var d = new Date();
        console.log(d + ': escpos_web socket closed');
    };

    escpos_web_print_result_socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const meet_to_tw_einvoice_standard = data.meet_to_tw_einvoice_standard;
        if (!meet_to_tw_einvoice_standard) {
            return false;
        }
        const batch_no = data.batch_no;
        const track_no = data.track_no;
        const status = data.status;
        var $tr = $('tr.data[batch_no='+batch_no+'][track_no='+track_no+']');
        if (0 >= $tr.length) {
            return false;
        }
        if (status) {
            var $prev_tr = $tr.prev('tr.data');
            if (0 < $prev_tr.length) {
                $('td[field=print_mark]', $prev_tr).text(pgettext('print_mark', 'Yes'));
            }
            $('td[field=status]', $tr).empty().append($('<i class="far fa-check-circle"></i>'));
        } else {
            const status_message = data.status_message;
            var fmts = ngettext('<p>It could not print E-Invoice successfully, please reboot the ESC/POS Printer server.</p><p>Error Detail: %(status_message)s</p>',
                                '<p>It could not print E-Invoice successfully, please reboot the ESC/POS Printer server.</p><p>Error Detail: %(status_message)s</p>',
                                1);
            var message = interpolate(fmts, {status_message: status_message}, true);
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$ERROR_MODAL,
                pgettext('taiwan_einvoice', 'ESC/POS Printer Error'),
                pgettext('taiwan_einvoice', message))
        }
    };
    escpos_web_print_result_socket.onopen = function(e) {
        $button.attr('escpos_web_print_result_socket', true);
        var d = new Date();
        console.log(d + ': escpos_web_print_result socket onopen');
    };
    escpos_web_print_result_socket.onerror = function(e) {
        $button.attr('escpos_web_print_result_socket', false);
        var d = new Date();
        console.log(d + ': escpos_web_print_result socket onerror');
    };
    escpos_web_print_result_socket.onclose = function(e) {
        $button.attr('escpos_web_print_result_socket', false);
        var d = new Date();
        console.log(d + ': escpos_web_print_result socket closed');
    };
    return {
        escpos_web_socket: escpos_web_socket,
        escpos_web_print_result_socket: escpos_web_print_result_socket
    };
};


function suspend_print_einvoice () {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        $modal.data('suspend', true);
        if ('modal' == $btn.attr('data-dismiss')) {
            //pass;
        } else {
            $btn.hide();
        }
        $('button.print_einvoice', $modal).show();
    }
};


function print_einvoice_each_by_each(allow_number, button_id) {
    var $button = $('#'+button_id);
    var $modal = $button.parents('.modal');
    if (allow_number != $modal.data('allow_number')) {
        console.log('allow_number: '+allow_number+'; modal allow_number: '+$modal.data('allow_number'));
        return false;
    }
    console.log('allow_number: '+allow_number+'; modal allow_number: '+$modal.data('allow_number'));
    var interval_seconds_of_printing = $('select[name=interval_seconds_of_printing]', $modal).val();
    var $td = $('td[field=status][value=""]:first', $modal);
    var $tr = $td.parents('tr');
    var $prev_tr = $tr.prev('tr.data');
    if (0 == window.WSS['escpos_web_socket'].readyState || 0 == window.WSS['escpos_web_print_result_socket'].readyState ) {
        console.log("Waiting successful connection");
        console.log("window.WSS['escpos_web_socket'].readyState: " + window.WSS['escpos_web_socket'].readyState);
        console.log("window.WSS['escpos_web_print_result_socket'].readyState: " + window.WSS['escpos_web_print_result_socket'].readyState);
        setTimeout('print_einvoice_each_by_each('+allow_number+', "'+button_id+'")', 500);
        return false;
    } else if ($modal.data('suspend') || 0 >= $td.length) {
        window.WSS['escpos_web_socket'].close();
        window.WSS['escpos_web_print_result_socket'].close();
        return false;
    } else if ($prev_tr.length >= 1 && $('.spinner-border', $prev_tr).length >= 1) {
        setTimeout('print_einvoice_each_by_each('+allow_number+', "'+button_id+'")', 500);
        return false;
    } else {
        if (0 < $prev_tr.length) {
            if (0 < $('i.fa-check-circle', $prev_tr).length) {
                $('td[field=print_mark]', $prev_tr).text(pgettext('print_mark', 'Yes'));
            } else {
                $('td[field=print_mark]', $prev_tr).empty();
            }
        }
        var $spinner = $('<div class="spinner-border text-primary" role="status">'
                         +'<span class="sr-only">'+gettext('Loading...')+'</span>'
                         +'</div>');
        var $suspend_button = $('<button type="button" class="btn btn-danger suspend_print_einvoice">'+pgettext("suspend_print_einvoice", "Suspend")+'</button>');
        var $re_print_original_copy = $('<button class="btn btn-info">'+gettext('Re-print original copy')+'</button>');
        $('td[field=print_mark]', $tr).append($re_print_original_copy);
        $td.empty().append($spinner);
        $td.attr('value', 'spinner');
        var $next_td = $('td[field=status][value=""]:first', $modal);
        $suspend_button.click(suspend_print_einvoice());
        $suspend_button.appendTo($next_td);

        var resource_uri = $modal.attr('resource_url_tmpl').replace('{id}', $tr.attr('einvoice_id'));
        var einvoice_printer_sn = $('select[name=einvoice_printer]', $modal).val();
        var details_printer_sn = $('select[name=details_printer]', $modal).val();
        var append_to_einvoice = $('input[name=append_to_einvoice]', $modal).prop('checked');
        if (append_to_einvoice) {
            resource_uri += '?with_details_content=true';
        }
        $.ajax({
            url: resource_uri,
            type: "GET",
            dataType: 'json',
            success: function (json) {
                var details_conent = json['details_content'];
                delete json['details_content'];
                var batch_no = Date.now();
                $tr.attr({batch_no: batch_no, track_no: json["track_no"]});
                window.WSS['escpos_web_socket'].send(JSON.stringify({
                    'serial_number': einvoice_printer_sn,
                    'batch_no': batch_no,
                    'invoice_json': JSON.stringify(json)
                }));
                if (append_to_einvoice && details_conent) {
                    var pdata = window.PRINTERS_DATA;
                    json['meet_to_tw_einvoice_standard'] = false;
                    json['width'] = pdata[details_printer_sn]['width'];
                    json['content'] = details_conent;
                    var batch_no = Date.now();
                    window.WSS['escpos_web_socket'].send(JSON.stringify({
                        'serial_number': details_printer_sn,
                        'batch_no': batch_no,
                        'invoice_json': JSON.stringify(json)
                    }));
                }
                setTimeout('print_einvoice_each_by_each('+allow_number+', "'+button_id+'")', parseInt(interval_seconds_of_printing));
            }
        });
    }
}


function print_einvoice (taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_result_url) {
    return function () {
        var $btn = $(this);
        var allow_number = Math.random();
        var $modal = $btn.parents('.modal');
        $modal.data({allow_number: allow_number, suspend: false});
        $('select, input', $modal).attr('disabled', 'disabled');
        if (window.WSS && 1 == window.WSS['escpos_web_socket'].readyState && 1 == window.WSS['escpos_web_print_result_socket'].readyState) {
            window.WSS['escpos_web_socket'].close();
            window.WSS['escpos_web_print_result_socket'].close();
        }
        window.WSS = build_two_websockets(taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_result_url, $btn);
        $btn.hide();
        print_einvoice_each_by_each(allow_number, $btn.attr('id'));
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

    $(".search").click(function () {
        var url_parts = window.location.href.split('?');
        var params = new URLSearchParams($('form:not(".language_form")').serialize());

        var result_url = url_parts[0] + '?' + params.toString();
        window.location.href = result_url;
    });
    $('select[name=einvoice_printer').change(function(){
        var value = $(this).val();
        Cookies.set(taiwan_einvoice_site.default_einvoice_printer_cookie_name, value, { path: '/' });
    });
    $('select[name=details_printer').change(function(){
        var value = $(this).val();
        Cookies.set(taiwan_einvoice_site.default_details_printer_cookie_name, value, { path: '/' });
    });
    $('input[name=append_to_einvoice').click(function(){
        var value = $(this).prop('checked');
        Cookies.set(taiwan_einvoice_site.default_append_to_einvoice_cookie_name, value, { path: '/' });
    });
    $('select[name=interval_seconds_of_printing').change(function(){
        var value = $(this).val();
        Cookies.set(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name, value, { path: '/' });
    });
    if ('true' == Cookies.get(taiwan_einvoice_site.default_append_to_einvoice_cookie_name)) {
        $('input[name=append_to_einvoice').prop('checked', 'checked');
    }
    if (Cookies.get(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name)) {
        $('select[name=interval_seconds_of_printing').val(Cookies.get(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name));
    }
    $('button.suspend_print_einvoice').click(suspend_print_einvoice());

    var escposweb_id_name = $.cookie.get(taiwan_einvoice_site.default_escposweb_cookie_name);
    if (escposweb_id_name){
        var escposweb_id = escposweb_id_name.split(':')[0];
        var escposweb_name = escposweb_id_name.split(':')[1].replace(/%3A/g, ':');
        var $btn = $('button.print_einvoice_modal');
        var ws_escposweb_status_url = $btn.attr('ws_escposweb_status_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_url = $btn.attr('ws_escposweb_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_print_result_url = $btn.attr('ws_escposweb_print_result_url_tmpl').replace('{id}', escposweb_id);
        $('span#default_escpos_print_name', $btn).text(escposweb_name);
        var $table = $('table.table');
        var $modal = $('#print_einvoice_modal');
        var $print_einvoice_button = $('.print_einvoice', $modal);
        $print_einvoice_button.click(print_einvoice(taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_result_url));
        $btn.removeClass('btn-danger').addClass('btn-secondary').click(function(){
            $('button.print_einvoice', $modal).show();
            $('select, input', $modal).removeAttr("disabled");
            if (0 >= $('img.status-on:visible').length) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNING_MODAL,
                    pgettext('taiwan_einvoice', 'Error'),
                    gettext('It can not connect ESC/POS Printer Server'));
                return false;
            } else if($('input[name=print_einvoice]:checked', $table).length == 0) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNING_MODAL,
                    pgettext('taiwan_einvoice', 'WARNING'),
                    gettext('Please choose one record at least'));
                return false;
            }
            var $modal_table = $('table', $modal);
            $('tbody tr.data', $modal_table).remove();
            var no = 1;
            $('input[name=print_einvoice]:checked', $table).each(function(){
                var $i = $(this);
                var $tr = $i.parents('tr');
                var $tr_tmpl = $('tr.tr_tmpl', $modal_table).clone().removeClass('tr_tmpl').addClass('data');
                $tr_tmpl.attr('einvoice_id', $tr.attr('einvoice_id'));
                $('td[field=no]', $tr_tmpl).text(no);
                var keys = [];
                $('td', $tr_tmpl).each(function(){
                    var field = $(this).attr('field');
                    if(field && field != 'no') {
                        keys.push(field);
                    }
                })
                for (var i=0; i<keys.length; i++) {
                    var value = $('td[field='+keys[i]+']', $tr).text();
                    $('td[field='+keys[i]+']', $tr_tmpl).attr('value', value).text(value);
                }
                $tr_tmpl.show().appendTo($('tbody', $modal_table));
                no += 1;
            });
            $modal.modal('show');
        });
        check_receive_escpos_printer_status_timestamp();
        set_up_the_escpos_printer(taiwan_einvoice_site, $btn, $modal, ws_escposweb_status_url);
    } else {
        $('button.print_einvoice_modal').removeClass('btn-secondary').addClass('btn-danger'
            ).text(gettext("Set up 'Default ESC/POS Printer first'")).click(function() {
            window.location = $(this).attr('set_up_default_escpos_printer_url');
        });
    }
});