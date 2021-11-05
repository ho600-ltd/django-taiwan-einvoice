function upload_csv_to_multiple_create_modal (taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $('#upload_csv_to_multiple_create_modal');
        $modal.modal('show');
    }
}


$(function () {
    $(".nav_sellerinvoicetrackno").addClass("nav_active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();

    adjust_pagination_html();

    $('button.upload_csv_to_multiple_create_modal').click(upload_csv_to_multiple_create_modal(taiwan_einvoice_site));
});