function show_canceleinvoice_modal(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $form = $btn.parents('form');
        var one_dimensional_barcode_for_canceling = $('[name=one_dimensional_barcode_for_canceling]', $form).val();
        var $modal = $('#show_canceleinvoice_modal');
        var resource_uri_tmpl = $modal.attr('resource_uri_tmpl');
        var resource_uri = resource_uri_tmpl.replace('{one_dimensional_barcode_for_canceling}', one_dimensional_barcode_for_canceling);
        $.ajax({
            url: resource_uri,
            type: "GET",
            dataType: 'json',
            contentType: 'application/json',
            success: function (json) {
                var $modal_table = $('table', $modal);
                $('tr.data', $modal_table).remove();
                for (var i=0; i<json['results'].length; i++) {
                    var einvoice = json['results'][i];
                    var kv = {
                        "year_month_range": einvoice['seller_invoice_track_no_dict']['year_month_range'],
                        "track_no_": einvoice['track_no_'],
                        "SalesAmount": einvoice['amounts']['SalesAmount'],
                        "TaxAmount": einvoice['amounts']['TaxAmount'],
                        "TotalAmount": einvoice['amounts']['TotalAmount'],
                        "generate_batch_no": einvoice['generate_batch_no']
                    }
                    var $tr_tmpl = $('tr.tr_tmpl', $modal_table).clone().removeClass('tr_tmpl').addClass('data');
                    $tr_tmpl.attr('einvoice_id', einvoice['id']);
                    $('td[field=no]', $tr_tmpl).text(i+1);
                    for (var k in kv) {
                        $('td[field="'+k+'"]', $tr_tmpl).attr('value', kv[k]).text(kv[k]);
                    }
                    $tr_tmpl.show().appendTo($('tbody', $modal_table));
                }
                $modal.modal('show');
            }
        });
    };
};


function cancel_einvoice(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var resource_uri = $modal.attr('resource_uri');
        var einvoice_id = $('tr.data', $modal).attr('einvoice_id');
        var reason = $('[name=reason]', $modal).val();
        var return_tax_document_number = $('[name=return_tax_document_number]', $modal).val();
        var remark = $('[name=remark]', $modal).val();
        if (reason && reason.length >=4 && reason.length <= 20){
            //pass
        } else {
            taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                gettext("Reason Error"),
                gettext("Limit from 4 to 20 words")
            );
            return false;
        }
        if (return_tax_document_number && return_tax_document_number.length <= 60){
            //pass
        } else if (!return_tax_document_number) {
            //pass
        } else {
            taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                gettext("Return Tax Document Number Error"),
                gettext("Limit to 60 words")
            );
            return false;
        }
        if (remark && remark.length <= 200){
            //pass
        } else if (!remark) {
            //pass
        } else {
            taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                gettext("Remark Error"),
                gettext("Limit to 200 words")
            );
            return false;
        }
        var re_create_einvoice = $('[name=re_create_einvoice]', $modal).is(":checked");
        $.ajax({
            url: resource_uri,
            type: "POST",
            data: {"einvoice_id": einvoice_id,
                   "reason": reason,
                   "return_tax_document_number": return_tax_document_number,
                   "remark": remark,
                   "re_create_einvoice": re_create_einvoice
                  },
            dataType: 'json',
            contentType: 'application/json',
            success: function (json) {
            }
        });
    };
};


$(function () {
    $(".nav_canceleinvoice").addClass("nav_active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();
    window.taiwan_einvoice_site = taiwan_einvoice_site;

    adjust_pagination_html();

    $('button.show_canceleinvoice_modal').click(show_canceleinvoice_modal(taiwan_einvoice_site));
    $('button.cancel_einvoice').click(cancel_einvoice(taiwan_einvoice_site));
});