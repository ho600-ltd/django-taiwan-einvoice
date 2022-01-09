$(function () {
    $('.dropdown-menu a').removeClass('active');
    $(".nav_permission").addClass("nav_active");
    $(".nav_turnkeywebgroup").addClass("active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();

    adjust_pagination_html();

});