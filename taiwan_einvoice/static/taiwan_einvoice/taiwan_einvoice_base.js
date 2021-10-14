function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}


function _N(str) {
    if (str) {
        return Number(str.toString().replace(/[^0-9\-\.]/, ''));
    } else {
        return 0;
    }
}


$(document).ajaxStart(function () {
    var static_url = $('input#static_url').val();
    if ($.blockUI) {
        $.blockUI({
            message: '<div class="loader">Loading...</div>',
            css: {
                'background-color': 'transparent',
                'border-color': 'transparent',
            },
        });
    }
}).ajaxStop(function () {
    if ($.unblockUI) {
        $.unblockUI();
    }
});


$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            var build_number = $.cookie('H6_BUILD_NUMBER');
            var version = $.cookie('H6_VERSION');
            var default_db_name_hash = $.cookie('H6_DEFAULT_DB_NAME_HASH');
            if (default_db_name_hash && build_number && version) {
                var csrftoken = $.cookie('csrftoken_' + default_db_name_hash + '_' + build_number + '_' + version);
            } else {
                var csrftoken = $.cookie('csrftoken');
            }
            if (typeof (csrftoken) == "undefined") {
                var csrftoken = $('input[name=csrfmiddlewaretoken]:first').val();
            }
            xhr.setRequestHeader("X-CSRFTOKEN", csrftoken);
        }
    }
});


function adjust_pagination_html() {
    $('.pagination_row li').addClass('page-item');
    $('.pagination_row li a').addClass('page-link');
}


function convert_time_str_to_iso8601_time_str(time_str) {
    var list = time_str.match(/(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/);
    if (list) {
        return list[1] + '-' + list[2] + '-' + list[3] + 'T' + list[4] + ':' + list[5] + ':' + list[6] + '+08:00';
    } else {
        return '';
    }
}


function pad(number) {
    if (number < 10) {
        return '0' + number;
    }
    return number;
}


function convert_iso8601_time_str_to_time_str(time) {
    return time.getFullYear() +
        '-' + pad(time.getMonth() + 1) +
        '-' + pad(time.getDate()) +
        ' ' + pad(time.getHours()) +
        ':' + pad(time.getMinutes()) +
        ':' + pad(time.getSeconds());
};