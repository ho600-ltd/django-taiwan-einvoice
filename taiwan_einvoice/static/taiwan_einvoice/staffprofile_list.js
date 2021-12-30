function create_staffprofile_modal (taiwan_einvoice_site) {
    return function () {
        var $modal = $('#create_staffprofile_modal');
        $modal.modal('show');
    }
}


function create_staffprofile (taiwan_einvoice_site) {
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
                    }
                    $('td[field="'+key+'"]', $tr).text(v);
                }
                $modal.modal('hide');
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
                    }
                    $('td[field="'+key+'"]', $tr).text(v);
                }
                $modal.modal('hide');
            }
        });
    }
}


$(function () {
    $(".nav_permission").addClass("nav_active");
    $('.dropdown-menu a').removeClass('active');
    $(".nav_staffprofile").addClass("active");

    taiwan_einvoice_site = new TAIWAN_EINVOICE_SITE('taiwan_einvoice_site', {
        $SUCCESS_MODAL: $('#success_modal'),
        $ERROR_MODAL: $('#error_modal'),
        $WARNING_MODAL: $('#warning_modal')
    });

    taiwan_einvoice_site.after_document_ready();
    window.taiwan_einvoice_site = taiwan_einvoice_site;

    adjust_pagination_html();

    $('button.create_staffprofile_modal').click(create_staffprofile_modal(taiwan_einvoice_site));
    $('button.create_staffprofile').click(create_staffprofile(taiwan_einvoice_site));
    $('button.update_staffprofile_modal').click(update_staffprofile_modal(taiwan_einvoice_site));
    $('button.update_staffprofile').click(update_staffprofile(taiwan_einvoice_site));
});