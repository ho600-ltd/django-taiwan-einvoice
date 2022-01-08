function remove_escposweboperator_modal (taiwan_einvoice_site) {
    return function() {
        var $btn = $(this);
        var $tr = $btn.parents('tr');
        var $operator = $btn.parents('.badge');
        var name = $('td[field=name]', $tr).text();
        var slug = $('td[field=slug]', $tr).text();
        var $modal = $('#remove_escposweboperator_modal');
        $('[field=name]', $modal).text(name);
        $('[field=slug]', $modal).text(slug);
        $('[field=operator]', $modal).text($operator.text());
        $modal.data({
            resource_uri: $tr.attr('resource_uri'),
            staffprofile_id: $operator.attr('staffprofile_id')
        })
        $modal.modal('show');
    };
};


function remove_escposweboperator(taiwan_einvoice_site) {
    return function() {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var resource_uri = $modal.data("resource_uri");
        var staffprofile_id = $modal.data("staffprofile_id");
        var data = {
            staffprofile_id: staffprofile_id,
            type: "remove"
        };
        $.ajax({
            url: resource_uri,
            type: "PATCH",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json',
            error: function (jqXHR, exception) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$ERROR_MODAL,
                    jqXHR['responseJSON']['error_title'],
                    jqXHR['responseJSON']['error_message'],
                );
            },
            success: function (json) {
                $modal.modal('hide');
                $('[staffprofile_id='+staffprofile_id+']').remove();
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    gettext("Removed")
                );
            }
        });
        $modal.modal('show');
    };
};


$(function () {
    $('.dropdown-menu a').removeClass('active');
    $(".nav_permission").addClass("nav_active");
    $(".nav_escposweboperator").addClass("active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();

    adjust_pagination_html();

    $('.remove_escposweboperator_modal').click(remove_escposweboperator_modal(taiwan_einvoice_site));
    $('.remove_escposweboperator').click(remove_escposweboperator(taiwan_einvoice_site));
});