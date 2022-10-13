$(function () {
    $(".nav_outgoingip").addClass("nav_active");

    escpos_web_site = new ESCPOS_PRINTER_SITE('escpos_web_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    escpos_web_site.after_document_ready();
    window.escpos_web_site = escpos_web_site;

    adjust_pagination_html();
});