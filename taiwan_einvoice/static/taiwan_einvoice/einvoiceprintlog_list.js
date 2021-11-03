$(function () {
    $(".nav_else").addClass("nav_active");
    $('.dropdown-menu a').removeClass('active');
    $(".nav_einvoiceprintlog").addClass("active");

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
});