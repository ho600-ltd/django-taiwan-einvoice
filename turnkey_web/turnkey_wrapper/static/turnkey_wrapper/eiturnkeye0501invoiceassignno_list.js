$(function () {
    $(".nav_E0501").addClass("nav_active");
    $('.dropdown-menu a').removeClass('active');
    $(".nav_EITurnkeyE0501InvoiceAssignNo").addClass("active");

    turnkey_wrapper_site = new turnkey_wrapper_site('turnkey_wrapper_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    turnkey_wrapper_site.after_document_ready();
    window.turnkey_wrapper_site = turnkey_wrapper_site;

    adjust_pagination_html();

});