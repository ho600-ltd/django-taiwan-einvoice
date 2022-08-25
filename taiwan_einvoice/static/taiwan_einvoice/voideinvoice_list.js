function show_voideinvoice_modal(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $form = $btn.parents('form');
        var one_dimensional_barcode_for_voiding = $('[name=one_dimensional_barcode_for_voiding]', $form).val();
        if (!one_dimensional_barcode_for_voiding) {
            taiwan_einvoice_site.show_modal(
                taiwan_einvoice_site.$WARNING_MODAL,
                gettext('Void E-Invoice Error'),
                gettext('Please type one-dimensional-barcode!')
                );
            return false;
        }
        var $modal = $('#show_voideinvoice_modal');
        var resource_uri_tmpl = $modal.attr('resource_uri_tmpl');
        var resource_uri = resource_uri_tmpl.replace('{one_dimensional_barcode_for_voiding}', one_dimensional_barcode_for_voiding);
        $.ajax({
            url: resource_uri,
            type: "GET",
            dataType: 'json',
            contentType: 'application/json',
            success: function (json) {
                var $modal_table = $('table', $modal);
                $('select, textarea, input', $modal).val('');
                $('input[type=text]', $modal).prop('disabled', true);
                $('input[type=checkbox]', $modal).prop("checked", false);
                $('tr.data', $modal_table).remove();
                if (0 >= json['results'].length) {
                    var fmts = ngettext("%(one_dimensional_barcode_for_voiding)s does not exist!",
                        "%(one_dimensional_barcode_for_voiding)s does not exist!",
                        1);
                    var message = interpolate(fmts, { one_dimensional_barcode_for_voiding: one_dimensional_barcode_for_voiding }, true);
                    taiwan_einvoice_site.show_modal(
                        taiwan_einvoice_site.$WARNING_MODAL,
                        gettext('E-Invoice Error'),
                        message
                    );
                    return false;
                }
                for (var i=0; i<json['results'].length; i++) {
                    var einvoice = json['results'][i];
                    if (einvoice['is_voided']) {
                        var fmts = ngettext("E-Invoice(%(track_no_)s) was already voided!",
                            "E-Invoice(%(track_no_)s) was already voided!",
                            1);
                        var message = interpolate(fmts, { track_no_: einvoice['track_no_'] }, true);
                        taiwan_einvoice_site.show_modal(
                            taiwan_einvoice_site.$WARNING_MODAL,
                            gettext('E-Invoice Error'),
                            message
                        );
                        return false;
                    } else if (!einvoice['can_void']) {
                        var fmts = ngettext("E-Invoice(%(track_no_)s) was already canceled and has created the new one!",
                            "E-Invoice(%(track_no_)s) was already canceled and has created the new one!",
                            1);
                        var message = interpolate(fmts, { track_no_: einvoice['track_no_'] }, true);
                        taiwan_einvoice_site.show_modal(
                            taiwan_einvoice_site.$WARNING_MODAL,
                            gettext('E-Invoice Error'),
                            message
                        );
                        return false;
                    }
                    var kv = {
                        "year_month_range": einvoice['seller_invoice_track_no_dict']['year_month_range'],
                        "track_no_": einvoice['track_no_'],
                        "buyer_identifier_npoban": einvoice['npoban'] ? einvoice['npoban'] : einvoice['buyer_identifier'],
                        "barcode": einvoice['carrier_id1'],
                        "SalesAmount": einvoice['amounts']['SalesAmount'],
                        "TaxAmount": einvoice['amounts']['TaxAmount'],
                        "TotalAmount": einvoice['amounts']['TotalAmount'],
                        "generate_no": einvoice['generate_no']
                    }
                                // <td field="buyer_identifier_npoban"></td>
                                // <td field="barcode"></td>
                    var $tr_tmpl = $('tr.tr_tmpl', $modal_table).clone().removeClass('tr_tmpl').addClass('data');
                    $tr_tmpl.attr('einvoice_id', einvoice['id']);
                    $('td[field=no]', $tr_tmpl).text(i+1);
                    for (var k in kv) {
                        var v = kv[k];
                        $('td[field="'+k+'"]', $tr_tmpl).attr('value', v).text(v);
                    }
                    $tr_tmpl.show().appendTo($('tbody', $modal_table));

                }
                if (einvoice['seller_invoice_track_no_dict']['turnkey_service_dict']['in_production']) {
                    $('#cancel_before_void', $modal).parents('div.form-check').hide();
                } else {
                    $('#cancel_before_void', $modal).parents('div.form-check').show();
                }
                $('[name=one_dimensional_barcode_for_voiding]', $form).val("");
                $modal.modal('show');
            }
        });
    };
};


function change_reason(taiwan_einvoice_site) {
    return function () {
        var $select = $(this);
        var $modal = $select.parents('.modal');
        var tags = $('option:selected', $select).attr('tags');
        $('input[name=buyer_identifier], input[name=npoban], input[name=mobile_barcode], input[name=natural_person_barcode]', $modal).each(function() {
            var $i = $(this);
            var name = $i.attr('name');
            if (tags && tags.indexOf(name) >= 0) {
                $i.prop('disabled', false);
            } else {
                $i.prop('disabled', true);
            }
        });
    };
};


function void_einvoice(taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var resource_uri = $modal.attr('resource_uri');
        var einvoice_id = $('tr.data', $modal).attr('einvoice_id');
        var reason = $('[name=reason]', $modal).val();
        var remark = $('[name=remark]', $modal).val();
        var cancel_before_void = $('[name=cancel_before_void]', $modal).prop('checked');
        var tags = $('[name=reason] option:selected', $modal).attr('tags').split(',');
        var updates = {
            "buyer_identifier": $('[name=buyer_identifier]', $modal).val(),
            "npoban": $('[name=npoban]', $modal).val(),
            "mobile_barcode": $('[name=mobile_barcode]', $modal).val(),
            "natural_person_barcode": $('[name=natural_person_barcode]', $modal).val()
        }
        if (reason && reason.length >=4 && reason.length <= 20){
            //pass
        } else {
            taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                gettext("Reason Error"),
                gettext("Please choose one of the reasons")
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
        var dev_null = [
            pgettext('void_reason_tag_name', 'buyer_identifier'),
            pgettext('void_reason_tag_name', 'npoban'),
            pgettext('void_reason_tag_name', 'mobile_barcode'),
            pgettext('void_reason_tag_name', 'natural_person_barcode')
        ];
        for (i=0; i<tags.length; i++) {
            if (!updates[tags[i]]) {
                var fmts = ngettext("Please input the new value of %(name)s depends on the reason!",
                        "Please input the new value of %(name)s depends on the reason!",
                        1);
                var message = interpolate(fmts, { name: pgettext('void_reason_tag_name', tags[i]) }, true);
                taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                    gettext("Void Error"),
                    message
                );
                return false;
            }
        }
        if (updates["buyer_identifier"] && updates["npoban"]) {
            taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                gettext("Buyer identifier/NPOBAN Error"),
                gettext("Do not set buyer identifier and npoban at the same time.")
            );
            return false;
        } else if (updates["mobile_barcode"] && updates["natural_person_barcode"]) {
            taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                gettext("Mobile/Natural Person barcode Error"),
                gettext("Do not set mobile and natural person barcode at the same time.")
            );
            return false;
        } else if (updates["natural_person_barcode"] && ! /[a-zA-Z][a-zA-z][0-9]{14}/.test(updates["natural_person_barcode"])) {
            taiwan_einvoice_site.show_modal(taiwan_einvoice_site.$WARNING_MODAL,
                gettext("Natural Person barcode Error"),
                gettext("Natural Person barcode should be prefixed two digits alphabets and follow 14 digits number.")
            );
            return false;
        }
        $.ajax({
            url: resource_uri,
            type: "POST",
            data: JSON.stringify({"einvoice_id": einvoice_id,
                   "reason": reason,
                   "remark": remark,
                   "buyer_identifier": updates["buyer_identifier"],
                   "npoban": updates["npoban"],
                   "mobile_barcode": updates["mobile_barcode"],
                   "natural_person_barcode": updates["natural_person_barcode"],
                   "cancel_before_void": cancel_before_void
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
                var message = gettext("Voided");
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    message
                );
                $('[name=reason], [name=remark]', $modal).val("");
                var kv = {
                    "no": gettext('NEW Record'),
                    "year_month_range": json['einvoice_dict']['seller_invoice_track_no_dict']['year_month_range'],
                    "track_no_": json['einvoice_dict']['track_no_'],
                    "einvoice_dict.random_number": json['einvoice_dict']['random_number'],
                    "new_einvoice_dict.random_number": json['new_einvoice_dict']['random_number'],
                    "type__display": json['einvoice_dict']['seller_invoice_track_no_dict']['type__display'],
                    "SalesAmount": json['einvoice_dict']['amounts']['SalesAmount'],
                    "TaxAmount": json['einvoice_dict']['amounts']['TaxAmount'],
                    "TotalAmount": json['einvoice_dict']['amounts']['TotalAmount'],
                    "generate_no": json['einvoice_dict']['generate_no'],
                    "creator_first_name_id": json['creator_dict']['first_name']+':'+json['creator_dict']['id'],
                    "generate_time": json['generate_time']
                };
                var $table = $('table.search_result');
                var s = '<tr>';
                $('thead tr th', $table).each(function(){
                    var $th = $(this);
                    var k = $th.attr('field');
                    if (k == "generate_time") {
                        s += '<td class="datetime" field="'+k+'" value="'+kv[k]+'" format="'+$th.attr('format')+'"></td>';
                    } else {
                        s += '<td field="'+k+'" value="'+kv[k]+'">'+kv[k]+'</td>';
                    }
                });
                s += '</tr>';
                $('tbody', $table).prepend($(s));
                $('.datetime', $table).each(taiwan_einvoice_site.convert_class_datetime(taiwan_einvoice_site));
            }
        });
    };
};


$(function () {
    $(".nav_else").addClass("nav_active");
    $('.dropdown-menu a').removeClass('active');
    $(".nav_voideinvoice").addClass("active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();
    window.taiwan_einvoice_site = taiwan_einvoice_site;

    adjust_pagination_html();

    $('select#reason').change(change_reason(taiwan_einvoice_site));
    $('button.show_voideinvoice_modal').click(show_voideinvoice_modal(taiwan_einvoice_site));
    $('button.void_einvoice').click(void_einvoice(taiwan_einvoice_site));
});