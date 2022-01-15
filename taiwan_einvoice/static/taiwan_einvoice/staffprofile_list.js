function add_staffprofile_modal (taiwan_einvoice_site) {
    return function () {
        var $modal = $('#add_staffprofile_modal');
        $('input[type=text]', $modal).val('');
        $('input[type=checkbox]', $modal).prop('checked', false);
        $modal.modal('show');
    }
}


function add_staffprofile (taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var resource_uri = $modal.attr('resource_uri');
        var data = {
            "user.username": $('input[name="user.username"]', $modal).val(),
            "nickname": $('input[name="nickname"]', $modal).val(),
            "is_active": $('input[name="is_active"]', $modal).prop('checked'),
            "in_printer_admin_group": $('input[name="in_printer_admin_group"]', $modal).prop('checked'),
            "in_manager_group": $('input[name="in_manager_group"]', $modal).prop('checked')
        };
        $.ajax({
            url: resource_uri,
            type: "POST",
            dataType: 'json',
            data: JSON.stringify(data),
            contentType: 'application/json',
            error: function (jqXHR, exception) {
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$ERROR_MODAL,
                    jqXHR['responseJSON']['error_title'],
                    jqXHR['responseJSON']['error_message'],
                );
            },
            success: function (json) {
                $('input', $modal).val('');
                $modal.modal('hide');
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    gettext("Created")
                );
                var kv = {
                    "no": gettext('NEW Record'),
                    "user.username": json['user_dict']['username'],
                    "nickname": json['nickname'],
                    "is_active": json['is_active'],
                    "in_printer_admin_group": json['in_printer_admin_group'],
                    "in_manager_group": json['in_manager_group'],
                    "groups": ""
                };
                var $table = $('table.search_result');
                var s = '<tr staffprofile_id="'+json['id']+'" resource_uri="'+json['resource_uri']+'">';
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
                    } else if ('user.username' == k) {
                        s += '<td field="'+k+'" value="'+kv[k]+'"><button class="btn btn-primary update_staffprofile_modal">'+kv[k]+'</button></td>';
                    } else {
                        s += '<td field="'+k+'" value="'+kv[k]+'">'+kv[k]+'</td>';
                    }
                });
                s += '</tr>';
                var $s = $(s);
                $('.update_staffprofile_modal', $s).click(update_staffprofile_modal(taiwan_einvoice_site));
                $('tbody', $table).prepend($s);
            }
        });
    }
}


function update_staffprofile_modal (taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $tr = $btn.parents('tr');
        var $modal = $('#update_staffprofile_modal');
        var resource_uri = $tr.attr('resource_uri');
        $modal.data('resource_uri', resource_uri);
        $.ajax({
            url: resource_uri,
            type: "GET",
            dataType: 'json',
            contentType: 'application/json',
            success: function (json) {
                var kv = {
                    "user.username": json['user_dict']['username'],
                    "nickname": json['nickname'],
                    "is_active": json['is_active'],
                    "in_printer_admin_group": json['in_printer_admin_group'],
                    "in_manager_group": json['in_manager_group']
                }
                $('input[type=text]', $modal).each(function(){
                    var name = $(this).attr('name');
                    $(this).val(kv[name]);
                });
                $('input[type=checkbox]', $modal).each(function(){
                    var name = $(this).attr('name');
                    if (kv[name]) {
                        $(this).prop('checked', true);
                    } else {
                        $(this).prop('checked', false);
                    }
                });
                $('.modal-body .group_set', $modal).remove();
                for (var k in json['groups']) {
                    var fmts = ngettext("Turnkey Web: %(name)s", "Turnkey Web: %(name)s", 1);
                    var turnkeyweb_name = interpolate(fmts, {name: k}, true);
                    var $turnkeyweb_div = $('<div class="form-group row group_set">'
                        +'<div class="col-sm-12"><p>'+turnkeyweb_name+'</p></div></div>');
                    $('.modal-body', $modal).append($turnkeyweb_div);
                    for (var i=0; i<json['groups'][k].length; i++) {
                        var g = json['groups'][k][i];
                        var $group_div = $('<div class="form-group row group_set">'
                            +'<div class="col-sm-2"><input type="checkbox" class="form-control" id="add_group_'+g['id']+'" name="add_group_'+g['id']+'" /></div>'
                            +'<div class="col-sm-10">'+g['display_name']+'</div>'
                            +'</div>');
                        if (g['is_member']) {
                            $('input[type=checkbox]', $group_div).prop('checked', true);
                        }
                        $('.modal-body', $modal).append($group_div);
                    }
                }
                $modal.modal('show');
            }
        });
    }
}


function update_staffprofile (taiwan_einvoice_site) {
    return function () {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var resource_uri = $modal.data('resource_uri');
        var data = {
            "nickname": $('input[name="nickname"]', $modal).val(),
            "is_active": $('input[name="is_active"]', $modal).prop('checked'),
            "in_printer_admin_group": $('input[name="in_printer_admin_group"]', $modal).prop('checked'),
            "in_manager_group": $('input[name="in_manager_group"]', $modal).prop('checked')
        };
        $('.group_set input[type=checkbox]', $modal).each(function(){
            var $i = $(this);
            data[$i.attr('name')] = $i.prop('checked');
        });
        $.ajax({
            url: resource_uri,
            type: "PATCH",
            dataType: 'json',
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: function (json) {
                var $tr = $('tr[resource_uri="'+resource_uri+'"]');
                for (var key in data) {
                    var v = data[key];
                    if ('is_active' == key) {
                        if (v) {
                            v = gettext('Actived');
                        } else {
                            v = '';
                        }
                    } else if ('in_printer_admin_group' == key) {
                        if (v) {
                            v = pgettext('in_printer_admin_group', 'Yes');
                        } else {
                            v = '';
                        }
                    } else if ('in_manager_group' == key) {
                        if (v) {
                            v = pgettext('in_manager_group', 'Yes');
                        } else {
                            v = '';
                        }
                    } else if ('groups' == key || 'count_within_groups' == key) {
                        continue;
                    }
                    $('td[field="'+key+'"]', $tr).text(v);
                }
                var s = '';
                $('td[field=groups]', $tr).html(s);
                var turnkeyweb_length = 0;
                for (var k in json['groups']) {
                    turnkeyweb_length += 1;
                }
                for (var k in json['groups']) {
                    var groups = json['groups'][k];
                    if (1 < turnkeyweb_length && 0 < json['count_within_groups'][k] ) {
                        s += k;
                    }
                    for (var i=0; i<groups.length; i++){
                        var group = groups[i];
                        if (group['is_member']) {
                            s += '<h5><span class="badge badge-pill badge-info" group_id="'+group['id']+'">'
                                +group['display_name']
                                +'</span></h5>';
                        }
                    }
                }
                $('td[field=groups]', $tr).html(s);
                $modal.modal('hide');
            }
        });
    }
}


$(function () {
    var $url = new URL(window.location.href);
    var ps = $url.pathname.split('/');
    var self_staffprofile = false;
    for (var i=0; i<ps.length-1; i++) {
        var name = ps[i+1];
        if (name.indexOf('.') >= 0) {
            var id = name.split('.')[0];
        } else {
            var id = name;
        }
        if (ps[i] == 'staffprofile' && parseInt(id) > 0) {
            self_staffprofile = true;
            break;
        }
    }
    $('.dropdown-menu a').removeClass('active');
    if (self_staffprofile) {
        $(".nav_self").addClass("nav_active");
        $(".nav_selfstaffprofile").addClass("active");
    } else {
        $(".nav_permission").addClass("nav_active");
        $(".nav_staffprofile").addClass("active");
    }

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();
    window.taiwan_einvoice_site = taiwan_einvoice_site;

    adjust_pagination_html();

    $('button.add_staffprofile_modal').click(add_staffprofile_modal(taiwan_einvoice_site));
    $('button.add_staffprofile').click(add_staffprofile(taiwan_einvoice_site));
    $('button.update_staffprofile_modal').click(update_staffprofile_modal(taiwan_einvoice_site));
    $('button.update_staffprofile').click(update_staffprofile(taiwan_einvoice_site));
    var dev_null = [
        pgettext('is_active', 'Yes')
    ]
});