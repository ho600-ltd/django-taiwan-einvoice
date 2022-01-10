function add_turnkeywebgroup_modal (taiwan_einvoice_site) {
    return function() {
        var $modal = $('#add_turnkeywebgroup_modal');
        $modal.modal('show');
    };
};


function add_turnkeywebgroup(taiwan_einvoice_site) {
    return function() {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var resource_uri = $modal.attr("resource_uri");
        var data = {
            display_name: $('input[name=display_name]', $modal).val(),
            type: "add_group"
        };
        if (!data['display_name']) {
            var title = gettext('Name Error');
            var message = gettext('Please type words in name');
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNING_MODAL,
                title,
                message
            );
            return false;
        }
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
                var tr_str = '<tr group_id="'+json['id']+'">'
                    + '<td>'+gettext('NEW RECORD')+'</td>'
                    + '<td><button class="btn btn-primary update_escposwebgroup">'+json['display_name']+'</button></td>'
                    + '<td></td></tr>';
                var $tr = $(tr_str);
                var $table = $('table.table');
                $('tbody', $table).prepend($tr);
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    gettext("Added")
                );
            }
        });
    };
};


function update_turnkeywebgroup_modal (taiwan_einvoice_site) {
    return function() {
        var $modal = $('#update_turnkeywebgroup_modal');
        $modal.modal('show');
    };
};


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

    $('.add_turnkeywebgroup_modal').click(add_turnkeywebgroup_modal(taiwan_einvoice_site));
    $('.add_turnkeywebgroup').click(add_turnkeywebgroup(taiwan_einvoice_site));
    $('.update_turnkeywebgroup_modal').click(update_turnkeywebgroup_modal(taiwan_einvoice_site));
});