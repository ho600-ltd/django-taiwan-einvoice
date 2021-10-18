$(function () {
    $(".nav_escposweb").addClass("nav_active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();

    adjust_pagination_html();

    $("button.search").click(function () {
        var url_parts = window.location.href.split('?');
        var params = new URLSearchParams($('form:not(".language_form")').serialize());

        var result_url = url_parts[0] + '?' + params.toString();
        window.location.href = result_url;
    });

    var usage_message = gettext('Default ESC/POS Printer');
    var show_default_escposweb_printer = function () {
        var default_escposweb_printer_id_name = Cookies.get(taiwan_einvoice_site.default_escposweb_printer_cookie_name);
        $('table tbody td[field=usage]').text('');
        if (default_escposweb_printer_id_name) {
            var default_escposweb_printer_id = default_escposweb_printer_id_name.split(':')[0];
            $('table tbody tr[escposweb_id='+default_escposweb_printer_id+'] td[field=usage]').text(usage_message);
        };
    };
    show_default_escposweb_printer();

    $('button.set_default_escposweb_printer').click(function(){
        Cookies.remove(taiwan_einvoice_site.default_escposweb_printer_cookie_name);
        var $btn = $(this);
        var $tr = $btn.parents('tr');
        var default_escposweb_printer_id = $tr.attr('escposweb_id');
        var default_escposweb_printer_id_name = default_escposweb_printer_id + ':' + $('td[field=name]', $tr).text();
        Cookies.set(taiwan_einvoice_site.default_escposweb_printer_cookie_name, default_escposweb_printer_id_name, { path: '/' });
        show_default_escposweb_printer();
    });
});