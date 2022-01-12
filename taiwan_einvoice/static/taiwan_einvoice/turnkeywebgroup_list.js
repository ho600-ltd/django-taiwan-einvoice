function add_turnkeywebgroup_modal (taiwan_einvoice_site) {
    return function() {
        var $modal = $('#add_turnkeywebgroup_modal');
        $('[name=display_name]', $modal).val('');
        $modal.modal('show');
    };
};


function add_turnkeywebgroup(taiwan_einvoice_site) {
    return function() {
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var resource_uri = $('#turnkeywebgroup').attr("resource_uri");
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
                    + '<td><button class="btn btn-primary update_turnkeywebgroup_modal">'+json['display_name']+'</button></td>'
                    + '<td></td></tr>';
                var $tr = $(tr_str);
                $('.update_turnkeywebgroup_modal', $tr).click(update_turnkeywebgroup_modal(taiwan_einvoice_site));
                var $table = $('table.search_result');
                $('tbody', $table).prepend($tr);
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    gettext("Added")
                );
                $('.total_count_row [field=count]').text($('tbody tr', $table).length);
            }
        });
    };
};


function update_turnkeywebgroup_modal (taiwan_einvoice_site) {
    return function() {
        var $modal = $('#update_turnkeywebgroup_modal');
        var $btn = $(this);
        var name = $btn.text();
        var $tr = $btn.parents('tr');
        $('[name=display_name]', $modal).val(name);
        $modal.data('group_id', $tr.attr('group_id'));
        $modal.data('permissions', $tr.attr('permissions'));
        $('input[type=checkbox]', $modal).each(function(){
            var $i = $(this);
            if (0 <= $modal.data('permissions').indexOf($i.attr('name'))) {
                $i.prop('checked', true);
            } else {
                $i.prop('checked', false);
            }
        });
        $('.modal-title', $modal).text(name);
        $modal.modal('show');
        var $lock_or_unlock_delete = $('.lock_or_unlock_delete', $modal);
        if($lock_or_unlock_delete.hasClass('fa-unlock')) {
            $lock_or_unlock_delete.click();
        }
    };
};


function update_turnkeywebgroup(taiwan_einvoice_site) {
    return function() {
        var resource_uri = $('#turnkeywebgroup').attr("resource_uri");
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var group_id = $modal.data('group_id');
        var permissions = {};
        $('input[type=checkbox]', $modal).each(function(){
            var $i = $(this);
            permissions[$i.attr('name')] = $i.prop('checked');
        });
        var data = {
            group_id: group_id,
            display_name: $('input[name=display_name]', $modal).val(),
            permissions: permissions,
            type: "update_group"
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
                $('tr[group_id="'+group_id+'"] td[field=name] button').text(data['display_name']);
                var p = '';
                for (var k in permissions) {
                    if (permissions[k]) {
                        p += k + ',';
                    }
                }
                $('tr[group_id="'+group_id+'"]').attr('permissions', p);
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    gettext("Updated")
                );
            }
        });
    };
};


function delete_turnkeywebgroup_modal (taiwan_einvoice_site) {
    return function() {
        var $delete_modal = $('#delete_turnkeywebgroup_modal');
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var group_id = $modal.data('group_id');
        $delete_modal.data('group_id', group_id);
        var name = $('.modal-title', $modal).text();
        var fmts = ngettext('Are you sure to delete "%s"?', 'Are you sure to delete "%s"?', 1);
        var message = interpolate(fmts, [name]);
        $('.message', $delete_modal).text(message);
        $modal.modal('hide');
        $delete_modal.modal('show');
    };
};


function delete_turnkeywebgroup(taiwan_einvoice_site) {
    return function() {
        var resource_uri = $('#turnkeywebgroup').attr("resource_uri");
        var $btn = $(this);
        var $modal = $btn.parents('.modal');
        var group_id = $modal.data('group_id');
        var data = {
            group_id: group_id,
            type: "delete_group"
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
                $('table.search_result tbody tr[group_id="'+group_id+'"]').remove();
                taiwan_einvoice_site.show_modal(
                    taiwan_einvoice_site.$SUCCESS_MODAL,
                    gettext("Success"),
                    gettext("Deleted")
                );
                var no = 1;
                $('table.search_result tbody tr').each(function(){
                    $('[field=no]', $(this)).text(no);
                    no += 1;
                });
                $('.total_count_row [field=count]').text(no);
            }
        });
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
    $('.update_turnkeywebgroup').click(update_turnkeywebgroup(taiwan_einvoice_site));
    $('.delete_turnkeywebgroup_modal').click(delete_turnkeywebgroup_modal(taiwan_einvoice_site));
    $('.delete_turnkeywebgroup').click(delete_turnkeywebgroup(taiwan_einvoice_site));
});