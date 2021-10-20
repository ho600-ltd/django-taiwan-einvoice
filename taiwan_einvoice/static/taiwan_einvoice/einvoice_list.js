function set_up_the_escpos_printer (taiwan_einvoice_site, $button, $modal, ws_escposweb_url, ws_escposweb_status_url, ws_escposweb_print_status_url) {
        if ('https:' == window.location.protocol) {
            var host = 'wss://' + window.location.host;
        } else {
            var host = 'ws://' + window.location.host;
        }

        const escpos_web_socket = new WebSocket(host+ws_escposweb_url);
        const escpos_web_status_socket = new WebSocket(host+ws_escposweb_status_url);
        const escpos_web_print_result_socket = new WebSocket(host+ws_escposweb_print_status_url);

        escpos_web_status_socket.onerror = function(e) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNINNG_MODAL,
                pgettext('taiwan_einvoice', 'WebSocket Connection Error'),
                gettext('Could not connect web server with websocket protocol.  It will cause printing job, except searching E-Invoice.  If you need to print E-Invoice, please try again later, or reload your page'));
            escpos_web_status_socket.close();
        };

        escpos_web_status_socket.onclose = function(e) {
            console.error('escpos_web_status socket closed unexpectedly');
            $('img.status-off', $button).show();
            $('img.status-on', $button).hide();
        };

        escpos_web_status_socket.onmessage = function(e) {
            $('img.status-on', $button).show();
            $('img.status-off', $button).hide();
            const data = JSON.parse(e.data);
            var $einvoice_printer = $('select[name=einvoice_printer]', $modal);
            var einvoice_printer_value = Cookies.get(taiwan_einvoice_site.default_einvoice_printer_cookie_name);
            var $details_printer = $('select[name=details_printer]', $modal);
            var details_printer_value = Cookies.get(taiwan_einvoice_site.default_details_printer_cookie_name);
            $('option', $einvoice_printer).remove();
            $('option', $details_printer).remove();
            for (k in data) {
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

        // escpos_web_socket.onmessage = function(e) {
        //     const data = JSON.parse(e.data);
        //     const invoice_data = JSON.parse(data.invoice_json);
        //     const ul = document.querySelector('#einvoice-invoice');
        //     const li = document.createElement("li");
        //     li.setAttribute("id", data.batch_no);
        //     li.appendChild(document.createTextNode(invoice_data.track_no));
        //     ul.prepend(li);
        // };

        // escpos_web_socket.onclose = function(e) {
        //     console.error('escpos_web socket closed unexpectedly');
        // };

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


$(function () {
    $(".nav_einvoice").addClass("nav_active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $WARNINNG_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();

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
        $('span#default_escpos_print_name', $btn).text(escposweb_name);
        var $table = $('table.table');
        var $modal = $('#print_einvoice_modal');
        $btn.removeClass('btn-danger').addClass('btn-secondary').click(function(){
            if (0 >= $('img.status-on:visible').length) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNINNG_MODAL,
                    pgettext('taiwan_einvoice', 'Error'),
                    gettext('It can not connect ESC/POS Printer Server'));
                return false;
            } else if($('input[name=print_einvoice]:checked', $table).length == 0) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNINNG_MODAL,
                    pgettext('taiwan_einvoice', 'Error'),
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
                var keys = ['year_month_range', 'track_no_', 'type__display', 'TotalAmount', 'generate_batch_no', 'print_mark'];
                for (var i=0; i<keys.length; i++) {
                    var value = $('td[field='+keys[i]+']', $tr).text();
                    $('td[field='+keys[i]+']', $tr_tmpl).attr('value', value).text(value);
                }
                $tr_tmpl.show().appendTo($('tbody', $modal_table));
                no += 1;
            });
            $modal.modal('show');
        });
        var ws_escposweb_url = $btn.attr('ws_escposweb_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_status_url = $btn.attr('ws_escposweb_status_url_tmpl').replace('{id}', escposweb_id);
        var ws_escposweb_print_status_url = $btn.attr('ws_escposweb_print_status_url_tmpl').replace('{id}', escposweb_id);
        set_up_the_escpos_printer(taiwan_einvoice_site, $btn, $modal, ws_escposweb_url, ws_escposweb_status_url, ws_escposweb_print_status_url);
    } else {
        $('button.print_einvoice_modal').removeClass('btn-secondary').addClass('btn-danger'
            ).text(gettext("Set up 'Default ESC/POS Printer first'")).click(function() {
            window.location = $(this).attr('set_up_default_escpos_printer_url');
        });
    }
});