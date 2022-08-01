$(function () {

    var TAIWAN_EINVOICE_SITE = function (name, configure) {
        if ('https:' == window.location.protocol) {
            this.WS_PROTOCOL = 'wss://' + window.location.host;
        } else {
            this.WS_PROTOCOL = 'ws://' + window.location.host;
        }
        this.name = name ? name : '__none__';
        this.second_offset = 0;
        this.DEFAULT_DATETIME_RE = new RegExp('^([0-9]+)-([0-9]+)-([0-9]+).([0-9]+):([0-9]+):([0-9]+)(\.[0-9]*)?Z?$');
        this.WEEKDAY = {
            0: gettext("Sun"), 1: gettext("Mon"), 2: gettext("Tue"), 3: gettext("Wen"),
            4: gettext("Thu"), 5: gettext("Fri"), 6: gettext("Sat"), 7: gettext("Sun")
        };
        this.MONTH = {
            1: gettext("Jan"), 2: gettext("Feb"), 3: gettext("Mar"), 4: gettext("Apr"),
            5: gettext("May"), 6: gettext("Jun"), 7: gettext("Jul"), 8: gettext("Aug"),
            9: gettext("Sep"), 10: gettext("Oct"), 11: gettext("Nov"), 12: gettext("Dec")
        }
        this.default_escposweb_cookie_name = 'default_escposweb';
        this.default_einvoice_printer_cookie_name = 'default_einvoice_printer';
        this.default_details_printer_cookie_name = 'default_details_printer';
        this.default_append_to_einvoice_cookie_name = 'default_append_to_einvoice';
        this.default_interval_seconds_of_printing_cookie_name = 'default_interval_seconds_of_printing';
        this.printer_receipt_type_width = {
            "5": "58mm",
            "6": "58mm",
            "8": "80mm"
        };
        this.datetimepicker_format = 'YYYY-MM-DD HH:mm:ss';
        this.django_datetime_format = 'Y-m-d H:i:s';

        for (var k in configure) {
            this[k] = configure[k];
        };

    };

    TAIWAN_EINVOICE_SITE.prototype.convert_tastypie_datetime = function (s) {
        var $self = this;
        var re = new RegExp('^([0-9]+)-([0-9]+)-([0-9]+).([0-9]+):([0-9]+):([0-9]+)(\.?[0-9]*)$');
        var list = re.exec(s);
        if (list) {
            return list[1]+'-'+list[2]+'-'+list[3]+' '+list[4]+':'+list[5]+':'+list[6];
        } else {
            var re = new RegExp('^([0-9]+)-([0-9]+)-([0-9]+)$');
            var list = re.exec(s);
            return list[1]+'-'+list[2]+'-'+list[3]+' 00:00:00';
        }
    };

    TAIWAN_EINVOICE_SITE.prototype.convert_time_from_utc_str = function (time_str, second_offset, display_format) {
        function in_02d (d) {
            if (d >= 0 && d <= 9) {
                return '0'+String(d);
            } else {
                return String(d);
            }
        };
        display_format = display_format ? display_format : 'Y-m-d H:i:s';

        var $self = this;
        if(!time_str){
            return '';
        }
        time_str = $self.convert_tastypie_datetime(time_str.replace(/Z$/, ''));
        var list = $self.DEFAULT_DATETIME_RE.exec(time_str);
        var D = Date.UTC(Number(list[1]), Number(list[2])-1, Number(list[3]),
                            Number(list[4]), Number(list[5]), Number(list[6]));
        var offseted_d = new Date(D + 1000*Number(second_offset));
        var Y = offseted_d.getUTCFullYear();
        var m = in_02d(offseted_d.getUTCMonth() + 1);
        var d = in_02d(offseted_d.getUTCDate());
        var H = in_02d(offseted_d.getUTCHours());
        var i = in_02d(offseted_d.getUTCMinutes());
        var s = in_02d(offseted_d.getUTCSeconds());
        var D = $self.WEEKDAY[Number(offseted_d.getUTCDay())];
        var M = $self.MONTH[Number(m)];
        var A = H >= 12 ? pgettext('timezone', 'PM') : pgettext('timezone', 'AM');
        return display_format.replace('Y', Y).replace('m', m).replace('d', d)
                            .replace('H', H).replace('i', i).replace('s', s)
                            .replace('D', D).replace('M', M).replace('A', A);
    };

    TAIWAN_EINVOICE_SITE.prototype.get_second_offset_by_timezone_id_value = function ($self) {
        var timezone = $('#timezone').attr('value');
        var second_offset = 0;
        if (timezone == 'Asia/Taipei'){
            second_offset = 28800;
        } else if (timezone == 'Asia/Tokyo'){
            second_offset = 32400;
        }
        return second_offset;
    };

    TAIWAN_EINVOICE_SITE.prototype.convert_class_datetime = function ($self) {
        return function() {
            var $span = $(this);
            var second_offset = $self.get_second_offset_by_timezone_id_value($self);
            if (second_offset != 0) {
                //pass
            } else if ($self.second_offset) {
                second_offset = $self.second_offset;
            } else {
                second_offset = 0;
            }
            if ($span.prop('tagName').toUpperCase() == 'INPUT') {
                var s = $self.convert_time_from_utc_str($span.attr('init_value'),
                                                        second_offset,
                                                        $span.attr('format'));
                $span.val(s);
            } else {
                var s = $self.convert_time_from_utc_str($span.attr('value'),
                                                        second_offset,
                                                        $span.attr('format'));
                $span.text(s);
            }
        };
    };

    TAIWAN_EINVOICE_SITE.prototype.show_modal = function ($modal, title, body) {
        $('.modal-title', $modal).html(title);
        body = body.replace(/\n/g, "<br/>");
        $('.modal-body', $modal).html(body);
        $modal.modal('show');
    };


    TAIWAN_EINVOICE_SITE.prototype.choose_all_check_in_the_same_td = function($self) {
        return function () {
            var $i = $(this);
            var $table = $i.parents('table');
            var field = $i.parents('th').attr('field');
            $('td[field='+field+']', $table).each(function(){
                $('td[field="'+field+'"] input', $(this).parents('tr')).prop('checked', $i.prop('checked'));
            });
        };
    };


    TAIWAN_EINVOICE_SITE.prototype.lock_or_unlock_delete = function ($self) {
        return function () {
            var $i = $(this);
            var $button = $('button.delete_modal', $i.parent());
            if($i.hasClass('fa-lock')) {
                $i.removeClass('fa-lock');
                $i.addClass('fa-unlock');
                $button.removeAttr('disabled');
            } else {
                $i.removeClass('fa-unlock');
                $i.addClass('fa-lock');
                $button.attr('disabled', 'disabled');
            }
        }
    };


    TAIWAN_EINVOICE_SITE.prototype.after_document_ready = function () {
        var $self = this;
        $('.datetime').each($self.convert_class_datetime($self));
        $.ajaxSetup({
            error: $self.rest_error($self, 'danger_modal')
        });
        var second_offset = $self.get_second_offset_by_timezone_id_value($self);
        var url = new URL(window.location.href);
        var datetime_kind_params = [
            'create_time__gte', 'create_time__lt',
            'update_time__gte', 'update_time__lt',
            'generate_time__gte', 'generate_time__lt',
            'print_time__gte', 'print_time__lt',
            'date_in_year_month_range'
        ];
        for (var param of datetime_kind_params) {
            var datetime_kind_param = $self.convert_time_from_utc_str(url.searchParams.get(param),
                                                                      second_offset,
                                                                      $self.django_datetime_format);
            if (datetime_kind_param) {
                var datetime_kind_time = new Date(datetime_kind_param);
                var datetime_kind_time_str = convert_iso8601_time_to_time_str(datetime_kind_time);
                $("input[name='"+param+"']").val(datetime_kind_time_str);
            }
        }
        for (var param of datetime_kind_params) {
            $('#'+param).datetimepicker({ format: $self.datetimepicker_format });
        }

        var string_kind_params = [
            'name__icontains',
            'nickname__icontains',
            'user__username__icontains',
            'slug__icontains',
            'track_no__icontains',
            'details__description__icontains',
            'code39__exact',
            'any_words__icontains',
            'einvoice__code39__exact',
            'id',
            'id_or_hex',
            'einvoice__track_no__icontains',
            'einvoice__any_words__icontains',
            'identifier__icontains',
            'seller__legal_entity__identifier__icontains',
            'batch__slug__icontains',
            'track__icontains'
        ];
        for (var param of string_kind_params) {
            var string_kind_param = url.searchParams.get(param);
            if (string_kind_param) {
                $("input[name='"+param+"']").val(string_kind_param);
            }
        }
        var select_kind_params = [
            'is_original_copy',
            'is_active',
            'print_mark',
            'carrier_type__regex',
            'npoban__regex',
            'ei_synced',
            'cancel_einvoice_type'
        ];
        for (var param of select_kind_params) {
            var select_kind_param = url.searchParams.get(param);
            if (select_kind_param) {
                $("select[name='"+param+"']").val(select_kind_param);
                $("select[name='"+param+"'] option[value='"+select_kind_param+"']").prop('selected', true);
            }
        }
        var gte_gt_lte_lt_kind_params = {
            "void_einvoice_type": ["reverse_void_order__gte=0", "reverse_void_order__lte=0", "reverse_void_order__gt=0"]
        }
        for (var key in gte_gt_lte_lt_kind_params) {
            for (var item of gte_gt_lte_lt_kind_params[key]) {
                param = item.split("=")[0];
                var value = url.searchParams.get(param);
                if (value) {
                    $("select[name='"+key+"']").val(item);
                    $("select[name='"+key+"'] option[value='"+item+"']").prop('selected', true);
                }
            }
        }

        $('.lock_or_unlock_delete').click($self.lock_or_unlock_delete($self));
        $('input.choose_all_check_in_the_same_td').click($self.choose_all_check_in_the_same_td($self));
        $("input[name='code39__exact']").click(function(){
            $(this).val('');
        }).focus();
        $("input[name='einvoice__code39__exact']").click(function(){
            $(this).val('');
        }).focus();

        $("button.search").click(function () {
            var url_parts = window.location.href.split('?');
            var $form = $(this).parents('form');
            if ($form.length <= 0) {
                var $form = $('form:not(".language_form")');
            }
            var params = new URLSearchParams($form.serialize());
            var second_offset = $self.get_second_offset_by_timezone_id_value();
            for (var k of params.keys()) {
                if ($('[name='+k+']', $form).hasClass('datetimepicker-input')) {
                    var value = $self.convert_time_from_utc_str(params.get(k),
                                                                -1 * second_offset,
                                                                $self.django_datetime_format);
                    params.set(k, value);
                } else if (gte_gt_lte_lt_kind_params[k]) {
                    var item = $('[name='+k+']', $form).val();
                    var _is = item.split('=');
                    params.set(_is[0], _is[1]);
                    params.delete(k);
                }
            }

            var result_url = url_parts[0] + '?' + params.toString();
            window.location.href = result_url;
        });

        $('td.record_order_no').each(function(){
            var $td = $(this);
            var init_page_no = $td.parents('table').attr('init_page_no');
            $td.text(parseInt(init_page_no) - parseInt($td.attr('counter0')));
        });
    }

    TAIWAN_EINVOICE_SITE.prototype.rest_error = function ($self, dialog_id) {
        return function (xhr, ajaxOptions, thrownError) {
            dialog_id = dialog_id ? dialog_id : 'error_dialog';
            var $modal = $('#' + dialog_id);
            if (xhr.status == 0) {
                var title = gettext('No Internet Connection');
                var html = gettext('<p>It seems that your internet connection has some problems. Please try again later.</p>');
            } else if (xhr.status == 500) {
                var debug = DEBUG;
                var title = 'HTTP ' + xhr.status;
                try {
                    var json = $.parseJSON(xhr.responseText);
                } catch (error) {
                    var json = xhr.responseText;
                    debug = false;
                }
                if (debug) {
                    var html = gettext('Error Code') + ' is <span class="notice"><a target="' + json['code'] + '" href="'
                        + BUGPAGE_URL + json['code'] + '/">' + json['code'] + '</a></span>';
                } else {
                    var html = '<h2>' + gettext('Error Code') + ': <span class="notice">' + json['code'] + '</span></h2>';
                }
            } else if (xhr.status == 401) {
                window.location = '/';
                return false;
            } else if (xhr.status == 400) {
                var json = $.parseJSON(xhr.responseText);
                var title = gettext('Error Code') + xhr.status + ': <br/>';
                var error_message = json['error_message'] ? json['error_message'] : json['detail'];
                var message = json['message'] ? json['message'] : json['detail'];
                if (error_message) {
                    var html = '<p>' + error_message + '</p>';
                } else if (message) {
                    var html = '<p>' + message + '</p>';
                }
            } else if (xhr.status == 403) {
                var json = $.parseJSON(xhr.responseText);
                var error_message = json['error_message'] ? json['error_message'] : json['detail'];
                var traceback = json['traceback'] ? json['traceback'] : json['detail'];
                var title = gettext('Error Code') + xhr.status + ': <br/>' + error_message;
                var html = '<pre style="color: red;">' + traceback + '</pre>';
                var width = 600;
            } else {
                var s = '';
                for (var k in json) {
                    s += k + ': ' + json[k];
                }
                try {
                    var traceback = $.parseJSON(xhr.responseText)['traceback'];
                } catch (error) {
                    var traceback = xhr.responseText;
                }
                var title = gettext('Error Code') + xhr.status + ': <br/>' + s;
                var html = '<pre style="color: red;">' + traceback + '</pre>';
            }
            $self.show_modal($modal, title, html);
        };
    };

    window.TAIWAN_EINVOICE_SITE = TAIWAN_EINVOICE_SITE;

});