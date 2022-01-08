function add_operators_to_escposweb_modal (taiwan_einvoice_site) {
    return function() {
        var $btn = $(this);
        var page = $btn.attr('page');
        var $tr = $btn.parents('tr');
        var name = $('td[field=name]', $tr).text();
        var slug = $('td[field=slug]', $tr).text();
        var $modal = $('#add_operators_to_escposweb_modal');
        $modal.modal('hide');
        var staffprofile_resource_uri = $('table.modal_table', $modal).attr('resource_uri');
        if ($tr && $tr.length > 0) {
            var existed_staffprofile_ids = [];
            $('.badge', $tr).each(function(){
                var staffprofile_id = $(this).attr('staffprofile_id');
                if (staffprofile_id) {
                    existed_staffprofile_ids.push(staffprofile_id);
                }
            });
            var escposweboperator_resource_uri = $tr.attr('resource_uri');
            $modal.data("resource_uri", escposweboperator_resource_uri);
            $modal.data("name", name);
            $modal.data("slug", slug);
            $modal.data("existed_staffprofile_ids", existed_staffprofile_ids);
        }
        $('[field=name]', $modal).text($modal.data("name"));
        $('[field=slug]', $modal).text($modal.data("slug"));
        var data = {
            page: page,
            page_size: 1000
        };
        if ('submit' == $btn.attr('type')) {
            var $form = $('form', $modal);
            $('input, select', $form).each(function(){
                var name = $(this).attr('name');
                data[name] = $(this).val();
            });
        }
        var params = [];
        for (var k in data) {
            params.push(k+'='+data[k]);
        }
        $.ajax({
            url: staffprofile_resource_uri+'?'+params.join('&'),
            type: "GET",
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
                var $table = $('table.modal_table', $modal);
                $('tbody tr', $table).remove();
                for (var i=0; i<json['results'].length; i++) {
                    var result = json['results'][i];
                    if (result['in_printer_admin_group']) {
                        var checkbox = gettext("Admin");
                    } else if (0 <= $modal.data("existed_staffprofile_ids").indexOf(String(result['id']))) {
                        var checkbox = gettext("Added");
                    } else {
                        var checkbox = '<input type="checkbox" />';
                    }
                    var kv = {
                        "no": i+1,
                        "checkbox": checkbox,
                        "user.username": result['user_dict']['username'],
                        "nickname": result['nickname'],
                        "is_active": result['is_active'],
                        "in_printer_admin_group": result['in_printer_admin_group'],
                        "in_manager_group": result['in_manager_group']
                    };
                    var s = '<tr staffprofile_id="'+result['id']+'">';
                    $('thead tr th', $table).each(function(){
                        var $th = $(this);
                        var k = $th.attr('field');
                        if ('boolean' == typeof(kv[k])) {
                            if (kv[k]) {
                                var value = pgettext(k, 'Yes');
                            } else {
                                var value = '';
                            }
                            s += '<td field="'+k+'">'+value+'</td>';
                        } else if ('checkbox' == k) {
                            s += '<td field="'+k+'">'+kv[k]+'</td>';
                        } else {
                            s += '<td field="'+k+'" value="'+kv[k]+'">'+kv[k]+'</td>';
                        }
                    });
                    s += '</tr>';
                    var $s = $(s);
                    $('tbody', $table).append($s);
                }
                $('[field=total_count]', $modal).text(json['count']);
                $modal.modal('show');
            }
        });
    };
};


function add_operators_to_escposweb(taiwan_einvoice_site) {
    return function() {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var resource_uri = $modal.data("resource_uri");
        var staffprofile_ids = [];
        $('input[type=checkbox]', $modal).each(function(){
            if ($(this).prop('checked')) {
                staffprofile_ids.push($(this).parents('tr').attr('staffprofile_id'));
            }
        });
        var data = {
            staffprofile_ids: staffprofile_ids,
            type: "add"
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
                var $tr = $('tr[resource_uri="'+resource_uri+'"]');
                $('[field=operators]', $tr).text('');
                for (var i=0; i<json['operators'].length; i++) {
                    var op = json['operators'][i];
                    var operator_str = '<h4 title="'+op['user_dict']['username']+'"><span class="badge badge-pill badge-success" staffprofile_id="'+op['id']+'">'
                        + op['nickname']
                        + '<a href="#" class="remove_operator_from_escposweb_modal"><i class="fas fa-user-times" style="color: red;"></i></a></span></h4>';
                    var $operator = $(operator_str);
                    $('.remove_operator_from_escposweb_modal', $operator).click(remove_operator_from_escposweb_modal(taiwan_einvoice_site));
                    $('[field=operators]', $tr).append($operator);
                }
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    gettext("Added")
                );
            }
        });
    };
};


function remove_operator_from_escposweb_modal (taiwan_einvoice_site) {
    return function() {
        var $btn = $(this);
        var $tr = $btn.parents('tr');
        var $operator = $btn.parents('.badge');
        var name = $('td[field=name]', $tr).text();
        var slug = $('td[field=slug]', $tr).text();
        var $modal = $('#remove_operator_from_escposweb_modal');
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


function remove_operator_from_escposweb(taiwan_einvoice_site) {
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

    $('.add_operators_to_escposweb_modal').click(add_operators_to_escposweb_modal(taiwan_einvoice_site));
    $('.add_operators_to_escposweb').click(add_operators_to_escposweb(taiwan_einvoice_site));
    $('.remove_operator_from_escposweb_modal').click(remove_operator_from_escposweb_modal(taiwan_einvoice_site));
    $('.remove_operator_from_escposweb').click(remove_operator_from_escposweb(taiwan_einvoice_site));
});