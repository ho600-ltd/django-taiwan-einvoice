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

    var escposweb_printer_id_name = $.cookie.get(taiwan_einvoice_site.default_escposweb_printer_cookie_name);
    if (escposweb_printer_id_name){
        var escposweb_printer_name = escposweb_printer_id_name.split(':')[1].replace(/%3A/g, ':');
        var $btn = $('button.print_einvoice_modal');
        $('span#default_escpos_print_name', $btn).text(escposweb_printer_name);
        var $table = $('table.table');
        $btn.click(function(){
            if($('input[name=print_einvoice]:checked', $table).length == 0) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$WARNINNG_MODAL,
                    pgettext('taiwan_einvoice', 'Error'),
                    gettext('Please choose one record at least'));
                return false;
            }
            var $modal = $('#print_einvoice_modal');

            var $modal_table = $('table', $modal);
            var no = 1;
            $('input[name=print_einvoice]:checked', $table).each(function(){
                var $i = $(this);
                var $tr = $i.parents('tr');
                var $tr_tmpl = $('tr.tr_tmpl', $modal_table).clone().removeClass('tr_tmpl');
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
    } else {
        $('button.print_einvoice_modal').text(gettext("Set up 'Default ESC/POS Printer first'")).click(function() {
            window.location = $(this).attr('set_up_default_escpos_printer_url');
        });
    }
});