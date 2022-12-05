function re_create_another_upload_batch_modal(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $tr = $btn.parents('tr');
        var obj_id = $tr.attr('obj_id');
        var $modal = $('#re_create_another_upload_batch_modal');
        $('[field=handling_note]', $modal).text('');
        $modal.data("obj_id", obj_id);
        $("td", $tr).each(function(){
            $td = $(this);
            var field = $td.attr('field');
            $('td[field="'+field+'"]', $modal).html($td.html());
        });
        $modal.modal('show');
    };
};


function re_create_another_upload_batch(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var obj_id = $modal.data('obj_id');
        var $tr = $('tr[obj_id="'+obj_id+'"]');
        var resource_uri = $modal.attr('resource_uri_tmpl').replace('/0/', '/'+obj_id+'/');
        var handling_type = $('[name=handling_type]', $modal).val();
        var handling_note = $('[name=handling_note]', $modal).val();
        if (handling_note && handling_note.length >=4 && handling_note.length <= 200){
            //pass
        } else {
            taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                gettext("Handling Note Error"),
                gettext("Limit from 4 to 200 words")
            );
            return false;
        }
        $.ajax({
            url: resource_uri,
            type: "POST",
            data: JSON.stringify({"handling_type": handling_type,
                   "handling_note": handling_note
                  }),
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
                $('td[field="pass_if_error"]', $tr).html(handling_note);
                var message = gettext("Created the new Upload Batch: ") + json['slug'];
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    message
                );
            }
        });
    };
};


$(function () {
    $(".nav_else").addClass("nav_active");
    $('.dropdown-menu a').removeClass('active');
    $(".nav_batcheinvoice").addClass("active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();
    window.taiwan_einvoice_site = taiwan_einvoice_site;

    adjust_pagination_html();

    $('button.re_create_another_upload_batch_modal').click(re_create_another_upload_batch_modal(taiwan_einvoice_site));
    $('button.re_create_another_upload_batch').click(re_create_another_upload_batch(taiwan_einvoice_site));
});