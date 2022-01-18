function show_default_escposweb (taiwan_einvoice_site) {
    var escposweb_cookie_name = taiwan_einvoice_site.default_escposweb_cookie_name;
    var pass_key_name = escposweb_cookie_name + '_pass_key';
    var usage_message = gettext('Default ESC/POS Printer');
    var default_escposweb_id_name = Cookies.get(escposweb_cookie_name);
    var pass_key = Cookies.get(pass_key_name);
    var pass_key_message = gettext('Pass Key: ') + pass_key;
    $('table tbody td[field=usage]').text('');
    if (default_escposweb_id_name) {
        var default_escposweb_id = default_escposweb_id_name.split(':')[0];
        var message = usage_message+'<br/>'+pass_key_message;
        $('table tbody tr[escposweb_id='+default_escposweb_id+'] td[field=usage]').html(message);
    };
};


function set_default_escposweb_modal (taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $tr = $btn.parents('tr');
        var $modal = $('#set_default_escposweb_modal');
        $('input[name=pass_key]', $modal).val('');
        $modal.data('escposweb_id', $tr.attr('escposweb_id'));
        $modal.modal('show');
    };
};


function set_default_escposweb (taiwan_einvoice_site) {
    return function () {
        var escposweb_cookie_name = taiwan_einvoice_site.default_escposweb_cookie_name;
        var pass_key_name = escposweb_cookie_name + '_pass_key';
        Cookies.remove(escposweb_cookie_name);
        Cookies.remove(pass_key_name);

        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var pass_key = $('input[name=pass_key]', $modal).val();
        var $tr = $('tr[escposweb_id="'+$modal.data('escposweb_id')+'"]');
        var default_escposweb_id = $tr.attr('escposweb_id');
        var default_escposweb_id_name = default_escposweb_id + ':' + $('td[field=name]', $tr).text();
        if (default_escposweb_id_name && !pass_key) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNING_MODAL,
                pgettext('taiwan_einvoice', 'Error'),
                gettext('Please input the "Pass Key"'));
            return false;
        }
        Cookies.set(escposweb_cookie_name, default_escposweb_id_name, { path: '/' });
        Cookies.set(pass_key_name, pass_key, { path: '/' });
        $modal.modal('hide');
        show_default_escposweb(taiwan_einvoice_site);
    };
};


$(function () {
    $(".nav_escposweb").addClass("nav_active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();

    adjust_pagination_html();

    show_default_escposweb(taiwan_einvoice_site);

    $('button.set_default_escposweb_modal').click(set_default_escposweb_modal(taiwan_einvoice_site));
    $('button.set_default_escposweb').click(set_default_escposweb(taiwan_einvoice_site));
});