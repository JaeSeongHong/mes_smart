// 대여등록, 회수, 현황 조회
function rental_list(done_callback) {
    $.ajax({
        url: "/rental/",
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

// 대여등록, 회수, 현황 조회
function rental_search(my_arr, done_callback) {
    $.ajax({
        url: "/rental/?master__code=" + my_arr[0] +
        "&master__item__name=" + my_arr[1] +
        "&master__item__model=" + my_arr[2] +
        "&master__item__version=" + my_arr[3] +
        "&master__rental_class=" + my_arr[4] +
        "&master__factory_class=" + my_arr[5],
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

// 대여등록, 회수, 현황 조회
function rental_status_search(my_arr, done_callback) {
    $.ajax({
        url: "/rental/?created_at_after=" + my_arr[0] +
        "&created_at_before=" + my_arr[1] +
        "&master__id=" + my_arr[2] +
        "&master__item__id=" + my_arr[3] +
        // "&master__item__model=" + my_arr[4] +
        // "&master__item__version=" + my_arr[5] +
        "&master__serial=" + my_arr[4] +
        "&customer__id=" + my_arr[5] +
        "&customer_name=" + my_arr[6],
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

// 대여품목관리 - 대여품목 조회
function rental_master_list(done_callback) {
    $.ajax({
        url: "/rental/master/",
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

// 대여품목관리 - 대여품목 조회
function rental_master_search(my_arr, done_callback) {
    $.ajax({
        url: "/rental/master/?id=" + my_arr[0] +
        "&item__id=" + my_arr[1] +
        // "&item__model__id=" + my_arr[2] +
        // "&item__version=" + my_arr[3] +
        "&rental_class__id=" + my_arr[2] +
        "&factory_class__id=" + my_arr[3],
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

// 대여품목관리 - 대여품목 조회 (개별)
function rental_master_read(code, done_callback) {
    $.ajax({
        url: "/rental/master/" + code + "/",
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}

// 대여등록, 회수, 현황 조회 (개별)
function rental_read(id, done_callback) {
    $.ajax({
        url: "/rental/" + id + "/",
        type: "GET",
        headers: {
            "Authorization": get_token()     // TODO: improve when replace it with something other one
        },
        xhrFields: {withCredentials: true},
    })
        .done(function (json) {
            // add cookie
            done_callback(json);
        })
        .fail(handle_error);
}