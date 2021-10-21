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
        escpos_web_status_socket.onerror = function(e) {
            var d = new Date();
            console.error(d + ': escpos_web_status socket connect fails');
            $('img.status-error', $button).show();
            $('img.status-on', $button).hide();
            $('img.status-off', $button).hide();
            if (!taiwan_einvoice_site.done_show_websocket_connection_error) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNING_MODAL,
                    pgettext('taiwan_einvoice', 'WebSocket Connection Error'),
                    gettext('<p>Could not connect web server with websocket protocol, now.  It will cause printing job, except searching E-Invoice.</p><p>If you need to print E-Invoice, please wait for the successful connection.</p>'));
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
                    taiwan_einvoice_site.show_modal(
                        taiwan_einvoice_site.$WARNING_MODAL,
                        pgettext('taiwan_einvoice', 'WebSocket Connection Error'),
                        gettext('<p>Could not connect web server with websocket protocol, now.  It will cause printing job, except searching E-Invoice.</p><p>If you need to print E-Invoice, please wait for the successful connection.</p>'));
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
            }
            if(einvoice_printer_value) {
                $('option[value='+einvoice_printer_value+']', $einvoice_printer).attr('selected', 'selected');
            }
            if (details_printer_value) {
                $('option[value='+details_printer_value+']', $details_printer).attr('selected', 'selected');
            }
        };
};


function build_two_websockets(taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_status_url, $button) {
    var $modal = $button.parents('.modal');
    const escpos_web_socket = new WebSocket(taiwan_einvoice_site.WS_PROTOCOL+ws_escposweb_url);
    const escpos_web_print_status_socket = new WebSocket(taiwan_einvoice_site.WS_PROTOCOL+ws_escposweb_print_status_url);
    escpos_web_socket.onopen = function(e) {
        $button.attr('escpos_web_socket', true);
    };
    escpos_web_socket.onerror = function(e) {
        $button.attr('escpos_web_socket', false);
    };
    escpos_web_socket.onclose = function(e) {
        var d = new Date();
        console.log(d + ': escpos_web socket closed');
    };
    escpos_web_socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const invoice_data = JSON.parse(data.invoice_json);
        const ul = document.querySelector('#einvoice-invoice');
        const li = document.createElement("li");
        li.setAttribute("id", data.batch_no);
        li.appendChild(document.createTextNode(invoice_data.track_no));
        ul.prepend(li);
    };
};


function print_einvoice (taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_status_url) {
    return function () {
        var $btn = $(this);
        var wss = build_two_websockets(taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_status_url, $btn);
        var escpos_web_socket = wss['escpos_web_socket'];
        var escpos_web_print_status_socket = wss['escpos_web_print_status_socket'];



        // document.querySelector('#einvoice-invoice-submit').onclick = function(e) {
        //     const invoiceInputDom = document.querySelector('#einvoice-invoice-input');
        //     const invoice_json = invoiceInputDom.value;
        //     if (invoice_json) {
        //         const batch_no = Math.random();
        //         escpos_web_socket.send(JSON.stringify({
        //             'serial_number': document.querySelector('#printer-serial_number').value,
        //             'batch_no': batch_no,
        //             'invoice_json': invoice_json
        //         }));
        //         invoiceInputDom.value = '';
        //     }
        // };


        // escpos_web_print_result_socket.onmessage = function(e) {
        //     const data = JSON.parse(e.data);
        //     const batch_no = data.batch_no;
        //     const track_no = data.track_no;
        //     const status = data.status;
        //     const li = document.getElementById(batch_no);
        //     if (status) {
        //         li.textContent = 'Done: ' + track_no;
        //     } else {
        //         const status_message = data.status_message;
        //         li.textContent = 'Fail: ' + track_no + ' => ' + status_message;
        //     }
        // };

        // escpos_web_print_result_socket.onclose = function(e) {
        //     console.error('escpos_web_print_result socket closed unexpectedly');
        // };



    };
};


$(function () {
    $(".nav_einvoice").addClass("nav_active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
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
        var value = $(this).val();
        Cookies.set(taiwan_einvoice_site.default_append_to_einvoice_cookie_name, value, { path: '/' });
    });
    $('select[name=interval_seconds_of_printing').change(function(){
        var value = $(this).val();
        Cookies.set(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name, value, { path: '/' });
    });
    if (Cookies.get(taiwan_einvoice_site.default_append_to_einvoice_cookie_name)) {
        $('input[name=append_to_einvoice').prop('checked', 'checked');
    }
    if (Cookies.get(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name)) {
        $('select[name=interval_seconds_of_printing').val(Cookies.get(taiwan_einvoice_site.default_interval_seconds_of_printing_cookie_name));
    }

    var escposweb_id_name = $.cookie.get(taiwan_einvoice_site.default_escposweb_cookie_name);
    if (escposweb_id_name){
        var escposweb_id = escposweb_id_name.split(':')[0];
        var escposweb_name = escposweb_id_name.split(':')[1].replace(/%3A/g, ':');
        var $btn = $('button.print_einvoice_modal');
        var ws_escposweb_status_url = $btn.attr('ws_escposweb_status_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_url = $btn.attr('ws_escposweb_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_print_status_url = $btn.attr('ws_escposweb_print_status_url_tmpl').replace('{id}', escposweb_id);
        $('span#default_escpos_print_name', $btn).text(escposweb_name);
        var $table = $('table.table');
        var $modal = $('#print_einvoice_modal');
        var $print_einvoice_button = $('.print_einvoice', $modal);
        $print_einvoice_button.click(print_einvoice(taiwan_einvoice_site, ws_escposweb_url, ws_escposweb_print_status_url));
        $btn.removeClass('btn-danger').addClass('btn-secondary').click(function(){
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