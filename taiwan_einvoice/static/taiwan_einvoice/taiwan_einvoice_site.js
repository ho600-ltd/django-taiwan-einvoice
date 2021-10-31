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

    TAIWAN_EINVOICE_SITE.prototype.convert_time_from_str = function (time_str, second_offset, display_format) {
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

    TAIWAN_EINVOICE_SITE.prototype.convert_class_datetime = function ($self) {
        return function() {
            var $span = $(this);
            var timezone = $('#timezone').attr('value');
            if (timezone == 'Asia/Taipei'){
                var second_offset = 28800;
            } else if ($self.second_offset) {
                var second_offset = $self.second_offset;
            } else {
                var second_offset = 0;
            }
            if ($span.prop('tagName').toUpperCase() == 'INPUT') {
                var s = $self.convert_time_from_str($span.attr('init_value'),
                                                    second_offset,
                                                    $span.attr('format'));
                $span.val(s);
            } else {
                var s = $self.convert_time_from_str($span.attr('value'),
                                                    second_offset,
                                                    $span.attr('format'));
                $span.text(s);
            }
        };
    };

    TAIWAN_EINVOICE_SITE.prototype.show_modal = function ($modal, title, body) {
        $('.modal-title', $modal).html(title);
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


    TAIWAN_EINVOICE_SITE.prototype.after_document_ready = function () {
        var $self = this;
        $('.datetime').each($self.convert_class_datetime($self));
        $.ajaxSetup({
            error: $self.rest_error($self, 'danger_modal')
        });

        var url = new URL(window.location.href);
        var create_time__gte_param = url.searchParams.get('create_time__gte');
        if (create_time__gte_param) {
            var create_time__gte_time = new Date(create_time__gte_param);
            var create_time__gte_time_str = convert_iso8601_time_str_to_time_str(create_time__gte_time);
            $("input[name='create_time__gte']").val(create_time__gte_time_str);
        }
        var create_time__lt_param = url.searchParams.get('create_time__lt');
        if (create_time__lt_param) {
            var create_time__lt_time = new Date(create_time__lt_param);
            var create_time__lt_time_str = convert_iso8601_time_str_to_time_str(create_time__lt_time);
            $("input[name='create_time__lt']").val(create_time__lt_time_str);
        }
        var update_time__gte_param = url.searchParams.get('update_time__gte');
        if (update_time__gte_param) {
            var update_time__gte_time = new Date(update_time__gte_param);
            var update_time__gte_time_str = convert_iso8601_time_str_to_time_str(update_time__gte_time);
            $("input[name='update_time__gte']").val(update_time__gte_time_str);
        }
        var update_time__lt_param = url.searchParams.get('update_time__lt');
        if (update_time__lt_param) {
            var update_time__lt_time = new Date(update_time__lt_param);
            var update_time__lt_time_str = convert_iso8601_time_str_to_time_str(update_time__lt_time);
            $("input[name='update_time__lt']").val(update_time__lt_time_str);
        }
        var generate_time__gte_param = url.searchParams.get('generate_time__gte');
        if (generate_time__gte_param) {
            var generate_time__gte_time = new Date(generate_time__gte_param);
            var generate_time__gte_time_str = convert_iso8601_time_str_to_time_str(generate_time__gte_time);
            $("input[name='generate_time__gte']").val(generate_time__gte_time_str);
        }
        var generate_time__lt_param = url.searchParams.get('generate_time__lt');
        if (generate_time__lt_param) {
            var generate_time__lt_time = new Date(generate_time__lt_param);
            var generate_time__lt_time_str = convert_iso8601_time_str_to_time_str(generate_time__lt_time);
            $("input[name='generate_time__lt']").val(generate_time__lt_time_str);
        }
        var name__icontains_param = url.searchParams.get('name__icontains');
        if (name__icontains_param) {
            $("input[name='name__icontains']").val(name__icontains_param);
        }
        var slug__icontains_param = url.searchParams.get('slug__icontains');
        if (slug__icontains_param) {
            $("input[name='slug__icontains']").val(slug__icontains_param);
        }
        var track_no__icontains_param = url.searchParams.get('track_no__icontains');
        if (track_no__icontains_param) {
            $("input[name='track_no__icontains']").val(track_no__icontains_param);
        }
        var details__description__icontains_param = url.searchParams.get('details__description__icontains');
        if (details__description__icontains_param) {
            $("input[name='details__description__icontains']").val(details__description__icontains_param);
        }
        var code39__exact_param = url.searchParams.get('code39__exact');
        if (code39__exact_param) {
            $("input[name='code39__exact']").val(code39__exact_param);
        }
        var any_words__icontains_param = url.searchParams.get('any_words__icontains');
        if (any_words__icontains_param) {
            $("input[name='any_words__icontains']").val(any_words__icontains_param);
        }

        $('#create_time__gte').datetimepicker({ format: 'YYYY-MM-DD HH:mm:ss' });
        $('#create_time__lt').datetimepicker({ format: 'YYYY-MM-DD HH:mm:ss' });
        $('#update_time__gte').datetimepicker({ format: 'YYYY-MM-DD HH:mm:ss' });
        $('#update_time__lt').datetimepicker({ format: 'YYYY-MM-DD HH:mm:ss' });
        $('#generate_time__gte').datetimepicker({ format: 'YYYY-MM-DD HH:mm:ss' });
        $('#generate_time__lt').datetimepicker({ format: 'YYYY-MM-DD HH:mm:ss' });

        $('input.choose_all_check_in_the_same_td').click($self.choose_all_check_in_the_same_td($self));
        $("input[name='code39__exact']").click(function(){
            $(this).val('');
        }).focus();
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